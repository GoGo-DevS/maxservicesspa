"""Convierte los correos de contacto@ en solicitudes del panel.

Cada correo termina en uno de estos casos:

- Aviso del formulario web          -> solicitud nueva (origen web) o se
                                       cuelga de la que ya registro la vista.
- Autorespuesta del formulario      -> se guarda, pero NO cuenta como respuesta.
- Correo de un cliente              -> se cuelga de su solicitud (mismo hilo o
                                       mismo remitente con una abierta) o abre una.
- Correo de Max al cliente          -> respuesta: marca la solicitud respondida.
- Correo de Max sin cliente (fda@)  -> reenvio interno, queda en la historia.
- Avisos de sistemas (Google, IG)   -> se ignoran.

Todo es idempotente por Message-ID: leer dos veces el mismo correo no duplica.
"""
from __future__ import annotations

import logging
import re
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from . import correo
from .vigencia import antes_del_corte
from .models import Evento, Mensaje, Sincronizacion, Solicitud

logger = logging.getLogger(__name__)

VENTANA_MISMO_CLIENTE = timedelta(days=30)
VENTANA_FORMULARIO = timedelta(minutes=20)
_RE_REENVIO = re.compile(r"^\s*(re|rv|fw|fwd)\s*:", re.I)


def _resumen():
    return {
        "leidos": 0, "nuevas": 0, "adjuntados": 0, "respuestas": 0,
        "reenvios": 0, "ya_estaban": 0, "omitidos": 0, "errores": 0,
    }


# ---------------------------------------------------------------- busquedas

def _por_hilo(m):
    ids = m.get("en_respuesta_a") or []
    if ids:
        previo = (
            Mensaje.objects.filter(message_id__in=ids)
            .select_related("solicitud")
            .order_by("-fecha")
            .first()
        )
        if previo:
            return previo.solicitud
    hilo = m.get("hilo")
    if hilo:
        s = Solicitud.objects.filter(gmail_hilo=hilo).order_by("recibida_en").first()
        if s:
            return s
        previo = Mensaje.objects.filter(gmail_hilo=hilo).select_related("solicitud").first()
        if previo:
            return previo.solicitud
    return None


def _abierta_de(direccion, fecha):
    return (
        Solicitud.objects.filter(
            cliente_email=direccion,
            recibida_en__gte=fecha - VENTANA_MISMO_CLIENTE,
            recibida_en__lte=fecha + VENTANA_FORMULARIO,
        )
        .exclude(estado__in=Solicitud.ESTADOS_CERRADOS)
        .order_by("-recibida_en")
        .first()
    )


def _web_cercana(direccion, fecha):
    return (
        Solicitud.objects.filter(
            origen=Solicitud.Origen.WEB,
            cliente_email=direccion,
            recibida_en__range=(fecha - VENTANA_FORMULARIO, fecha + VENTANA_FORMULARIO),
        )
        .order_by("recibida_en")
        .first()
    )


def _guardar(solicitud, m, sentido, automatico=False, **cambios):
    datos = dict(m, **cambios)
    msj = Mensaje.objects.create(
        solicitud=solicitud,
        message_id=datos["message_id"],
        sentido=sentido,
        automatico=automatico,
        de=datos["de"][:254],
        de_nombre=(datos.get("nombre") or "")[:160],
        para=", ".join(datos.get("para") or []),
        cc=", ".join(datos.get("cc") or []),
        asunto=(datos.get("asunto") or "")[:300],
        extracto=(datos.get("cuerpo") or "")[: correo.TOPE_EXTRACTO],
        adjuntos=datos.get("adjuntos") or [],
        fecha=datos["fecha"],
        gmail_hilo=datos.get("hilo") or "",
    )
    campos = []
    if not solicitud.gmail_hilo and msj.gmail_hilo:
        solicitud.gmail_hilo = msj.gmail_hilo
        campos.append("gmail_hilo")
    if sentido == Mensaje.Sentido.ENTRANTE and (
        solicitud.actividad_en is None or msj.fecha > solicitud.actividad_en
    ):
        solicitud.actividad_en = msj.fecha
        campos.append("actividad_en")
    if campos:
        solicitud.save(update_fields=campos + ["actualizada_en"])
    return msj


# ---------------------------------------------------------------- casos

def _aviso_formulario(m, r):
    cliente = correo.cliente_del_formulario(m)
    if not cliente:
        r["omitidos"] += 1
        return
    s = _web_cercana(cliente, m["fecha"])
    cuerpo = m["cuerpo"]
    if s is None and antes_del_corte(m["fecha"]):
        r["omitidos"] += 1
        return
    if s is None:
        servicio = correo.campo_formulario(cuerpo, "Servicio requerido")
        s = Solicitud.objects.create(
            origen=Solicitud.Origen.WEB,
            categoria=Solicitud.Categoria.COTIZACION,
            cliente_email=cliente,
            cliente_nombre=correo.campo_formulario(cuerpo, "Nombre")[:160],
            cliente_empresa=correo.campo_formulario(cuerpo, "Empresa o proyecto")[:160],
            cliente_telefono=correo.campo_formulario(cuerpo, "Telefono")[:40],
            servicio=servicio[:80],
            ubicacion=correo.campo_formulario(cuerpo, "Ubicacion")[:160],
            asunto=("Formulario web" + (f": {servicio}" if servicio else ""))[:300],
            detalle=correo.mensaje_formulario(cuerpo),
            recibida_en=m["fecha"],
            esperando_desde=m["fecha"],
            actividad_en=m["fecha"],
            gmail_hilo=m.get("hilo") or "",
        )
        s.registrar(Evento.Tipo.CREADA, "Llegó por el formulario de la web")
        r["nuevas"] += 1
    elif s.mensajes.filter(sentido=Mensaje.Sentido.ENTRANTE).exists():
        # La vista ya la registro al enviarse el formulario: no se duplica.
        if not s.gmail_hilo and m.get("hilo"):
            s.gmail_hilo = m["hilo"]
            s.save(update_fields=["gmail_hilo", "actualizada_en"])
        r["ya_estaban"] += 1
        return
    _guardar(
        s, m, Mensaje.Sentido.ENTRANTE,
        de=cliente, nombre=s.cliente_nombre, cuerpo=s.detalle or cuerpo,
    )


def _autorespuesta(m, r):
    s = None
    for d in m["para"]:
        if not correo.es_propio(d):
            s = _web_cercana(d, m["fecha"]) or _abierta_de(d, m["fecha"])
            if s:
                break
    if s is None:
        r["omitidos"] += 1
        return
    _guardar(s, m, Mensaje.Sentido.SALIENTE, automatico=True)


def _saliente(m, r):
    externos = [d for d in m["para"] + m["cc"] if not correo.es_propio(d)]
    s = _por_hilo(m)
    if s is None:
        for d in externos:
            s = _abierta_de(d, m["fecha"])
            if s:
                break
    if s is None:
        r["omitidos"] += 1
        return
    if s.cliente_email in externos:
        _guardar(s, m, Mensaje.Sentido.SALIENTE)
        if s.marcar_respondida(m["fecha"], m["de"]):
            r["respuestas"] += 1
        else:
            r["adjuntados"] += 1
        return
    # Sale de Max pero no le llega al cliente: un reenvio a fda@ o a un tercero.
    _guardar(s, m, Mensaje.Sentido.INTERNO)
    destino = ", ".join(m["para"] + m["cc"]) or "sin destinatario"
    s.registrar(Evento.Tipo.REENVIO, f"Reenviado a {destino}")
    r["reenvios"] += 1


def _entrante(m, r):
    s = _por_hilo(m) or _abierta_de(m["de"], m["fecha"])
    if s is not None:
        _guardar(s, m, Mensaje.Sentido.ENTRANTE)
        if s.esperando_desde is None and s.categoria != Solicitud.Categoria.OTRO:
            s.esperando_desde = m["fecha"]
            s.save(update_fields=["esperando_desde", "actualizada_en"])
        s.registrar(Evento.Tipo.CLIENTE, f"Escribió {m['de']}")
        r["adjuntados"] += 1
        return
    if antes_del_corte(m["fecha"]):
        r["omitidos"] += 1
        return
    categoria = correo.clasificar(m["asunto"], m["cuerpo"], m.get("masivo", False))
    s = Solicitud.objects.create(
        origen=Solicitud.Origen.CORREO,
        categoria=categoria,
        cliente_email=m["de"],
        cliente_nombre=(m.get("nombre") or "")[:160],
        asunto=m["asunto"][:300],
        detalle=m["cuerpo"],
        recibida_en=m["fecha"],
        esperando_desde=None if categoria == Solicitud.Categoria.OTRO else m["fecha"],
        actividad_en=m["fecha"],
        gmail_hilo=m.get("hilo") or "",
    )
    _guardar(s, m, Mensaje.Sentido.ENTRANTE)
    s.registrar(
        Evento.Tipo.CREADA,
        f"Llegó por correo ({Solicitud.Categoria(categoria).label.lower()})",
    )
    r["nuevas"] += 1


def procesar(m: dict, r: dict) -> None:
    """Ubica un correo ya parseado. `r` acumula el resumen."""
    r["leidos"] += 1
    if Mensaje.objects.filter(message_id=m["message_id"]).exists():
        r["ya_estaban"] += 1
        return
    if m.get("fecha") is None:
        m["fecha"] = timezone.now()
    asunto = (m.get("asunto") or "").lower()
    reenvio = bool(_RE_REENVIO.match(asunto))
    if correo.es_propio(m["de"]):
        if correo.ASUNTO_FORMULARIO in asunto and not reenvio:
            return _aviso_formulario(m, r)
        if correo.ASUNTO_AUTORESPUESTA in asunto and not reenvio:
            return _autorespuesta(m, r)
        return _saliente(m, r)
    if correo.es_sistema(m["de"]):
        r["omitidos"] += 1
        return
    return _entrante(m, r)


def procesar_lote(mensajes, r=None):
    r = r or _resumen()
    ahora = timezone.now()
    for m in sorted(mensajes, key=lambda x: (x.get("fecha") or ahora, x.get("uid") or 0)):
        try:
            with transaction.atomic():
                procesar(m, r)
        except Exception:
            logger.exception("Panel: no se pudo procesar el correo %s", m.get("message_id"))
            r["errores"] += 1
    return r


# ---------------------------------------------------------------- formulario

def registrar_formulario(contact_request, ids=None):
    """La vista de contacto llama esto apenas se guarda el formulario, para que
    la solicitud aparezca en el panel sin esperar a leer el correo. `ids` trae
    los Message-ID con que salieron el aviso interno y la autorespuesta: asi la
    lectura del correo los reconoce y no duplica nada."""
    ids = ids or {}
    try:
        return contact_request.solicitud_panel
    except Solicitud.DoesNotExist:
        pass
    email_cliente = (contact_request.email or "").strip().lower()
    s = _web_cercana(email_cliente, contact_request.created_at)
    if s is not None and s.contact_request_id is None:
        s.contact_request = contact_request
        s.save(update_fields=["contact_request", "actualizada_en"])
        return s
    servicio = contact_request.get_service_display()
    s = Solicitud.objects.create(
        origen=Solicitud.Origen.WEB,
        categoria=Solicitud.Categoria.COTIZACION,
        contact_request=contact_request,
        cliente_email=email_cliente,
        cliente_nombre=contact_request.full_name[:160],
        cliente_empresa=(contact_request.company or "")[:160],
        cliente_telefono=(contact_request.phone or "")[:40],
        servicio=servicio[:80],
        ubicacion=(contact_request.location or "")[:160],
        asunto=f"Formulario web: {servicio}"[:300],
        detalle=contact_request.message,
        recibida_en=contact_request.created_at,
        esperando_desde=contact_request.created_at,
        actividad_en=contact_request.created_at,
    )
    s.registrar(Evento.Tipo.CREADA, "Llegó por el formulario de la web")
    Mensaje.objects.create(
        solicitud=s,
        message_id=ids.get("aviso") or f"<formulario-{contact_request.pk}@panel.{correo.DOMINIO}>",
        sentido=Mensaje.Sentido.ENTRANTE,
        de=email_cliente,
        de_nombre=contact_request.full_name[:160],
        para=getattr(settings, "CONTACT_EMAIL", ""),
        asunto=s.asunto,
        extracto=contact_request.message[: correo.TOPE_EXTRACTO],
        fecha=contact_request.created_at,
    )
    if ids.get("confirmacion"):
        Mensaje.objects.create(
            solicitud=s,
            message_id=ids["confirmacion"],
            sentido=Mensaje.Sentido.SALIENTE,
            automatico=True,
            de=getattr(settings, "DEFAULT_FROM_EMAIL", ""),
            para=email_cliente,
            asunto="Hemos recibido tu solicitud | MAX SERVICES SPA",
            extracto="Autorespuesta del formulario.",
            fecha=contact_request.created_at,
        )
    return s


def registrar_formulario_seguro(contact_request, ids=None):
    """El formulario de la web no puede fallar por culpa del panel."""
    try:
        with transaction.atomic():
            return registrar_formulario(contact_request, ids)
    except Exception:
        logger.exception("Panel: no se pudo registrar el formulario %s", contact_request.pk)
        return None


def importar_formularios_pendientes(dias=None):
    """Formularios guardados que no quedaron en el panel (por ejemplo, si el
    registro fallo). Devuelve cuantos se agregaron."""
    from core.models import ContactRequest

    dias = dias or getattr(settings, "PANEL_DIAS_INICIALES", 45)
    desde = timezone.now() - timedelta(days=dias)
    from .vigencia import desde as corte

    if corte() and corte() > desde:
        desde = corte()
    nuevos = 0
    for cr in ContactRequest.objects.filter(
        created_at__gte=desde, solicitud_panel__isnull=True
    ):
        if registrar_formulario_seguro(cr):
            nuevos += 1
    return nuevos


# ---------------------------------------------------------------- corrida

def sincronizar(lector=None, dias=None, maximo=400):
    """Lee lo nuevo de la casilla y lo ubica. Devuelve el resumen."""
    estado = Sincronizacion.actual()
    dias = dias or getattr(settings, "PANEL_DIAS_INICIALES", 45)
    lector = lector or correo.LectorImap()
    r = _resumen()
    mensajes, uids = [], []
    try:
        with lector as L:
            uidvalidity = L.uidvalidity()
            continuar = estado.ultimo_uid and estado.uidvalidity == uidvalidity
            desde = estado.ultimo_uid + 1 if continuar else 0
            uids = L.uids(desde, dias)[:maximo]
            for uid in uids:
                m = L.traer(uid)
                if m:
                    mensajes.append(m)
            carpeta = L.carpeta
    except Exception as exc:
        estado.ultimo_error = f"{exc.__class__.__name__}: {exc}"[:500]
        estado.ultima_corrida = timezone.now()
        estado.save(update_fields=["ultimo_error", "ultima_corrida"])
        raise
    procesar_lote(mensajes, r)
    r["formularios"] = importar_formularios_pendientes(dias)
    estado.carpeta = carpeta
    estado.uidvalidity = uidvalidity
    if uids:
        estado.ultimo_uid = max(uids)
    estado.ultima_corrida = timezone.now()
    estado.ultimo_error = ""
    estado.save()
    return r
