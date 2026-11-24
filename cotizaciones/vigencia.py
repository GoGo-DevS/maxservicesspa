"""Fecha de corte del panel (PANEL_DESDE)."""
from datetime import datetime
from zoneinfo import ZoneInfo

from django.conf import settings


def desde():
    """Medianoche (hora de Chile) del dia PANEL_DESDE, o None si no hay corte."""
    valor = getattr(settings, "PANEL_DESDE", "") or ""
    if not valor:
        return None
    try:
        dia = datetime.strptime(valor, "%Y-%m-%d")
    except ValueError:
        return None
    return dia.replace(tzinfo=ZoneInfo(settings.TIME_ZONE))


def vigentes(qs):
    corte = desde()
    return qs.filter(actividad_en__gte=corte) if corte else qs


def antes_del_corte(fecha):
    corte = desde()
    return bool(corte and fecha and fecha < corte)
