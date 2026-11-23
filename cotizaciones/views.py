import logging
import re
from datetime import timedelta
from statistics import median

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import avisos, correo
from .models import Evento, Sincronizacion, Solicitud
from .permisos import panel_requerido, responde, sin_indexar
from .sincronizar import sincronizar

logger = logging.getLogger(__name__)

PESTANAS = [
    ("por_responder", "Por responder"),
    ("en_curso", "En curso"),
    ("cerradas", "Cerradas"),
    ("otros", "Otros correos"),
    ("todas", "Todas"),
]


# ---------------------------------------------------------------- utilidades

def _filtro(ver):
    base = Solicitud.objects.all()
    no_otro = ~Q(categoria=Solicitud.Categoria.OTRO)
    abiertas = ~Q(estado__in=Solicitud.ESTADOS_CERRADOS)
    if ver == "por_responder":
        return base.filter(no_otro, abiertas, esperando_desde__isnull=False).order_by(
            "esperando_desde"
        )
    if ver == "en_curso":
        return base.filter(no_otro, abiertas, esperando_desde__isnull=True)
    if ver == "cerradas":
        return base.filter(estado__in=Solicitud.ESTADOS_CERRADOS)
    if ver == "otros":
        return base.filter(categoria=Solicitud.Categoria.OTRO)
    return base


def _hace(fecha, ahora):
    if not fecha:
        return ""
    seg = max(0, (ahora - fecha).total_seconds())
    if seg < 3600:
        return f"hace {max(1, int(seg // 60))} min"
    if seg < 86400:
        return f"hace {int(seg // 3600)} h"
    dias = int(seg // 86400)
    return "ayer" if dias == 1 else f"hace {dias} días"


def _nivel(dias):
    if dias is None:
        return "ok"
    if dias >= avisos.umbral():
        return "rojo"
    if dias >= avisos.umbral() / 2:
        return "ambar"
    return "verde"


def _dias_txt(dias):
    if dias is None:
        return ""
    if dias < 1 / 24:
        return "recién"
    if dias < 1:
        return f"{int(round(dias * 24))} h"
    if abs(dias - round(dias)) < 0.05:
        n = int(round(dias))
        return "1 día" if n == 1 else f"{n} días"
    return f"{dias:.1f} días".replace(".", ",")


def _gmail_url(solicitud):
    if not solicitud.gmail_hilo:
        return ""
    try:
        hilo = format(int(solicitud.gmail_hilo), "x")
    except ValueError:
        return ""
    cuenta = getattr(settings, "PANEL_IMAP_USER", "") or "0"
    return f"https://mail.google.com/mail/u/?authuser={cuenta}#all/{hilo}"


def _whatsapp(telefono):
    digitos = re.sub(r"\D", "", telefono or "")
    if len(digitos) == 9 and digitos.startswith("9"):
        digitos = "56" + digitos
    if len(digitos) == 11 and digitos.startswith("56"):
        return f"https://wa.me/{digitos}"
    return ""


def _sincronizar_si_corresponde(request):
    if not getattr(settings, "PANEL_SINCRONIZAR_AL_ABRIR", True) or not correo.hay_credencial():
        return
    estado = Sincronizacion.actual()
    minutos = getattr(settings, "PANEL_SINCRONIZAR_CADA_MIN", 5)
    if estado.ultima_corrida and timezone.now() - estado.ultima_corrida < timedelta(minutes=minutos):
        return
    try:
        sincronizar(maximo=150)
    except Exception as exc:
        logger.warning("Panel: la sincronizacion al abrir fallo: %s", exc)
        messages.warning(request, "No se pudo leer el correo recién. Se muestra lo último guardado.")


# ---------------------------------------------------------------- vistas

@panel_requerido
def bandeja(request):
    _sincronizar_si_corresponde(request)
    ahora = timezone.now()
    ver = request.GET.get("ver", "por_responder")
    if ver not in dict(PESTANAS):
        ver = "por_responder"
    q = (request.GET.get("q") or "").strip()[:80]

    qs = _filtro(ver).select_related("vista_por").annotate(num_mensajes=Count("mensajes"))
    if q:
        qs = qs.filter(
            Q(cliente_nombre__icontains=q)
            | Q(cliente_email__icontains=q)
            | Q(cliente_empresa__icontains=q)
            | Q(asunto__icontains=q)
        )
    pagina = Paginator(qs, 40).get_page(request.GET.get("pagina"))
    filas = []
    for s in pagina.object_list:
        dias = avisos.dias_habiles(s.esperando_desde, ahora) if s.esperando_desde else None
        filas.append(
            {
                "s": s,
                "hace": _hace(s.recibida_en, ahora),
                "dias": dias,
                "dias_txt": _dias_txt(dias),
                "nivel": _nivel(dias) if s.categoria != Solicitud.Categoria.OTRO else "ok",
            }
        )

    pendientes = list(
        _filtro("por_responder").values_list("esperando_desde", "categoria")
    )
    vencidas = sum(
        1
        for desde, cat in pendientes
        if cat == Solicitud.Categoria.COTIZACION
        and avisos.dias_habiles(desde, ahora) >= avisos.umbral()
    )
    respondidas = list(
        Solicitud.objects.filter(
            respondida_en__gte=ahora - timedelta(days=30),
        )
        .exclude(categoria=Solicitud.Categoria.OTRO)
        .values_list("recibida_en", "respondida_en")
    )
    tiempos = [avisos.dias_habiles(a, b) for a, b in respondidas if a and b]
    conteos = {
        clave: _filtro(clave).count() for clave in ("por_responder", "en_curso", "otros")
    }
    estado = Sincronizacion.actual()
    return render(
        request,
        "cotizaciones/bandeja.html",
        {
            "filas": filas,
            "pagina": pagina,
            "ver": ver,
            "q": q,
            "pestanas": [(k, v, conteos.get(k)) for k, v in PESTANAS],
            "stats": {
                "por_responder": conteos["por_responder"],
                "vencidas": vencidas,
                "respondidas_7": sum(
                    1 for _, b in respondidas if b and b >= ahora - timedelta(days=7)
                ),
                "mediana": _dias_txt(median(tiempos)) if tiempos else "",
            },
            "sync": estado,
            "sync_hace": _hace(estado.ultima_corrida, ahora) if estado.ultima_corrida else "",
            "hay_credencial": correo.hay_credencial(),
        },
    )


@panel_requerido
def detalle(request, pk):
    s = get_object_or_404(Solicitud.objects.select_related("vista_por"), pk=pk)
    ahora = timezone.now()
    if responde(request.user) and s.vista_en is None:
        s.vista_en = ahora
        s.vista_por = request.user
        campos = ["vista_en", "vista_por", "actualizada_en"]
        if s.estado == Solicitud.Estado.NUEVA:
            s.estado = Solicitud.Estado.VISTA
            campos.append("estado")
        s.save(update_fields=campos)
        s.registrar(Evento.Tipo.VISTA, f"La abrió {_nombre(request.user)}", request.user)
    dias = avisos.dias_habiles(s.esperando_desde, ahora) if s.esperando_desde else None
    return render(
        request,
        "cotizaciones/detalle.html",
        {
            "s": s,
            "mensajes": s.mensajes.all(),
            "eventos": s.eventos.select_related("usuario").order_by("-creado_en", "-pk"),
            "dias": dias,
            "dias_txt": _dias_txt(dias),
            "nivel": _nivel(dias),
            "hace": _hace(s.recibida_en, ahora),
            "gmail_url": _gmail_url(s),
            "whatsapp_url": _whatsapp(s.cliente_telefono),
            "etapas": [
                (v, l) for v, l in Solicitud.Estado.choices if v != Solicitud.Estado.NUEVA
            ],
            "categorias": Solicitud.Categoria.choices,
        },
    )


def _nombre(user):
    return user.get_full_name() or user.get_username()


@require_POST
@panel_requerido
def accion(request, pk):
    s = get_object_or_404(Solicitud, pk=pk)
    tipo = request.POST.get("accion", "")
    valor = request.POST.get("valor", "")
    quien = _nombre(request.user)
    ahora = timezone.now()

    if tipo == "estado" and valor in Solicitud.Estado.values:
        if valor == Solicitud.Estado.RESPONDIDA:
            s.marcar_respondida(ahora, quien, request.user, f"{quien} la marcó como respondida")
            s.refresh_from_db()
            if s.estado != Solicitud.Estado.RESPONDIDA:
                s.estado = Solicitud.Estado.RESPONDIDA
                s.save(update_fields=["estado", "actualizada_en"])
        else:
            anterior = s.get_estado_display()
            s.estado = valor
            campos = ["estado", "actualizada_en"]
            if valor != Solicitud.Estado.VISTA:
                # Cotizada, Ganada o Perdida: el cliente ya no espera nada de Max.
                s.esperando_desde = None
                campos.append("esperando_desde")
            s.save(update_fields=campos)
            s.registrar(
                Evento.Tipo.ESTADO, f"{anterior} → {s.get_estado_display()}", request.user
            )
        messages.success(request, f"Etapa: {s.get_estado_display()}.")
    elif tipo == "categoria" and valor in Solicitud.Categoria.values:
        s.categoria = valor
        campos = ["categoria", "actualizada_en"]
        if valor == Solicitud.Categoria.OTRO:
            s.esperando_desde = None
            campos.append("esperando_desde")
        elif s.esperando_desde is None and s.respondida_en is None and not s.cerrada:
            s.esperando_desde = s.recibida_en
            campos.append("esperando_desde")
        s.save(update_fields=campos)
        s.registrar(Evento.Tipo.CATEGORIA, s.get_categoria_display(), request.user)
        messages.success(request, f"Marcada como: {s.get_categoria_display()}.")
    elif tipo == "nota":
        texto = (request.POST.get("texto") or "").strip()
        if texto:
            s.registrar(Evento.Tipo.NOTA, texto, request.user)
            messages.success(request, "Nota guardada.")
    else:
        messages.error(request, "Acción no reconocida.")
    return redirect("cotizaciones:detalle", pk=s.pk)


@require_POST
@panel_requerido
def sincronizar_ahora(request):
    try:
        r = sincronizar()
    except correo.FaltaCredencial as exc:
        messages.error(request, str(exc))
    except Exception as exc:
        logger.exception("Panel: sincronizacion manual")
        messages.error(request, f"No se pudo leer el correo: {exc.__class__.__name__}.")
    else:
        messages.success(
            request,
            f"Correo leído: {r['nuevas']} nuevas, {r['respuestas']} respuestas detectadas.",
        )
    return redirect("cotizaciones:bandeja")


@csrf_exempt
@require_POST
def tarea(request):
    """La llama el cron de GitHub Actions: lee el correo y manda los avisos."""
    esperado = getattr(settings, "PANEL_CRON_TOKEN", "")
    recibido = request.headers.get("X-Panel-Token", "")
    if not esperado or not constant_time_compare(recibido, esperado):
        return sin_indexar(JsonResponse({"ok": False}, status=403))
    salida = {"ok": True}
    try:
        salida["sincronizacion"] = sincronizar()
    except Exception as exc:
        logger.exception("Panel: sincronizacion del cron")
        salida["ok"] = False
        salida["sincronizacion"] = {"error": exc.__class__.__name__}
    try:
        salida["avisos"] = avisos.enviar_avisos()
    except Exception as exc:
        logger.exception("Panel: avisos del cron")
        salida["ok"] = False
        salida["avisos"] = {"error": exc.__class__.__name__}
    return sin_indexar(JsonResponse(salida, status=200 if salida["ok"] else 500))


# ---------------------------------------------------------------- sesion

INTENTOS_MAX = 8
INTENTOS_VENTANA = 15 * 60


def _ip(request):
    reenviada = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return (reenviada.split(",")[0].strip() if reenviada else "") or request.META.get(
        "REMOTE_ADDR", ""
    )


class Entrar(auth_views.LoginView):
    template_name = "cotizaciones/entrar.html"
    redirect_authenticated_user = True

    def _clave(self):
        return f"panel-entrar:{_ip(self.request)}"

    def post(self, request, *args, **kwargs):
        if cache.get(self._clave(), 0) >= INTENTOS_MAX:
            # Ni siquiera se revisa la clave: el bloqueo corta antes.
            contexto = self.get_context_data(form=self.form_class(request=request), bloqueado=True)
            return sin_indexar(self.render_to_response(contexto, status=429))
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        clave = self._clave()
        cache.set(clave, cache.get(clave, 0) + 1, INTENTOS_VENTANA)
        return sin_indexar(super().form_invalid(form))

    def get_default_redirect_url(self):
        return reverse("cotizaciones:bandeja")

    def get(self, request, *args, **kwargs):
        return sin_indexar(super().get(request, *args, **kwargs))


class Salir(auth_views.LogoutView):
    next_page = reverse_lazy("cotizaciones:entrar")


class PedirClave(auth_views.PasswordResetView):
    template_name = "cotizaciones/clave_pedir.html"
    email_template_name = "cotizaciones/emails/clave.txt"
    subject_template_name = "cotizaciones/emails/clave_asunto.txt"
    success_url = reverse_lazy("cotizaciones:clave_enviada")
    extra_email_context = {"marca": "Max Services"}


class ClaveEnviada(auth_views.PasswordResetDoneView):
    template_name = "cotizaciones/clave_enviada.html"


class NuevaClave(auth_views.PasswordResetConfirmView):
    template_name = "cotizaciones/clave_nueva.html"
    success_url = reverse_lazy("cotizaciones:clave_lista")


class ClaveLista(auth_views.PasswordResetCompleteView):
    template_name = "cotizaciones/clave_lista.html"
