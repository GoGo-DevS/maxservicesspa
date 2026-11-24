"""Aviso de cotizaciones sin respuesta.

Dos veces al dia habil (9:00 y 15:00 por defecto) sale un correo a Felipe con
las cotizaciones que llevan mas de un dia habil esperando respuesta. Un solo
correo con la lista, no uno por solicitud: el aviso tiene que leerse, no
convertirse en otra bandeja que se ignora.

Dias habiles = lunes a viernes, hora de Chile. Los feriados cuentan como dia
habil (simplificacion consciente: a lo mas adelanta un aviso).
"""
from __future__ import annotations

from datetime import timedelta, timezone as dt_timezone
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from .models import Evento, Sincronizacion, Solicitud
from .vigencia import vigentes


def _chile():
    return ZoneInfo(settings.TIME_ZONE)


def dias_habiles(desde, hasta) -> float:
    """Tiempo entre dos instantes contando solo de lunes a viernes."""
    if desde is None or hasta is None or hasta <= desde:
        return 0.0
    zona = _chile()
    cursor = desde.astimezone(zona)
    fin = hasta.astimezone(zona)
    segundos = 0.0
    while cursor < fin:
        manana = (cursor + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        tramo = min(manana, fin)
        if cursor.weekday() < 5:
            segundos += (
                tramo.astimezone(dt_timezone.utc) - cursor.astimezone(dt_timezone.utc)
            ).total_seconds()
        if tramo <= cursor:  # resguardo ante un cambio de hora raro
            break
        cursor = tramo
    return segundos / 86400


def umbral():
    return float(getattr(settings, "PANEL_AVISO_DIAS_HABILES", 1))


def vencidas(ahora=None):
    """Cotizaciones abiertas cuyo cliente espera hace mas del umbral."""
    ahora = ahora or timezone.now()
    limite = umbral()
    qs = (
        vigentes(Solicitud.objects.all()).filter(
            esperando_desde__isnull=False,
            categoria=Solicitud.Categoria.COTIZACION,
        )
        .exclude(estado__in=Solicitud.ESTADOS_CERRADOS)
        .order_by("esperando_desde")
    )
    return [s for s in qs if dias_habiles(s.esperando_desde, ahora) >= limite]


def turno(ahora=None):
    """'2026-11-23T09' si `ahora` cae en una hora de aviso de un dia habil."""
    local = (ahora or timezone.now()).astimezone(_chile())
    horas = getattr(settings, "PANEL_AVISO_HORAS", [9, 15])
    if local.weekday() >= 5 or local.hour not in horas:
        return None
    return local.strftime("%Y-%m-%dT%H")


def _url(solicitud):
    return settings.SITE_URL.rstrip("/") + reverse("cotizaciones:detalle", args=[solicitud.pk])


def enviar_avisos(ahora=None, forzar=False):
    ahora = ahora or timezone.now()
    estado = Sincronizacion.actual()
    t = turno(ahora)
    if not forzar:
        if t is None:
            return {"enviado": False, "motivo": "fuera del horario de avisos"}
        if estado.ultimo_aviso_turno == t:
            return {"enviado": False, "motivo": "ya se avisó en este turno"}
    para = list(getattr(settings, "PANEL_AVISO_PARA", []))
    cc = list(getattr(settings, "PANEL_AVISO_CC", []))
    if not para:
        return {"enviado": False, "motivo": "sin destinatario (PANEL_AVISO_PARA)"}
    lista = vencidas(ahora)
    if not lista:
        if t:
            estado.ultimo_aviso_turno = t
            estado.save(update_fields=["ultimo_aviso_turno"])
        return {"enviado": False, "motivo": "nada vencido", "cantidad": 0}

    filas = [
        {
            "solicitud": s,
            "dias": dias_habiles(s.esperando_desde, ahora),
            "url": _url(s),
        }
        for s in lista
    ]
    n = len(filas)
    asunto = (
        "1 cotización espera respuesta hace más de un día hábil"
        if n == 1
        else f"{n} cotizaciones esperan respuesta hace más de un día hábil"
    )
    contexto = {
        "filas": filas,
        "cantidad": n,
        "panel_url": settings.SITE_URL.rstrip("/") + reverse("cotizaciones:bandeja"),
    }
    mensaje = EmailMultiAlternatives(
        asunto,
        render_to_string("cotizaciones/emails/aviso.txt", contexto),
        settings.DEFAULT_FROM_EMAIL,
        para,
        cc=cc,
    )
    mensaje.attach_alternative(
        render_to_string("cotizaciones/emails/aviso.html", contexto), "text/html"
    )
    mensaje.send(fail_silently=False)

    destino = ", ".join(para)
    for fila in filas:
        s = fila["solicitud"]
        s.ultimo_aviso_en = ahora
        s.save(update_fields=["ultimo_aviso_en", "actualizada_en"])
        s.registrar(Evento.Tipo.AVISO, f"Aviso de demora enviado a {destino}")
    estado.ultimo_aviso_turno = t or ahora.astimezone(_chile()).strftime("%Y-%m-%dT%H")
    estado.save(update_fields=["ultimo_aviso_turno"])
    return {"enviado": True, "cantidad": n, "para": para}
