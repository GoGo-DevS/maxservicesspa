"""Navidad 2026: la decide el SERVIDOR por fecha (version 2, 17-11-2026).

La v1 dependia solo de un JavaScript que agregaba la clase despues de pintar.
En la v2 la franja de saludo, la guirnalda y el gorro salen en el HTML desde el
primer pintado: no mueven nada (CLS 0) y se ven aunque el navegador no corra
JavaScript. El JS queda solo para la nieve que cae.

Fuera de la ventana no se agrega NADA: ni la franja, ni la hoja de estilos de
Navidad, ni el script. Se apaga sola; no hace falta otro despliegue.

PARA SACARLA ANTES: sacar "core.navidad.contexto" de TEMPLATES en settings.
PARA EL PROXIMO ANO: cambiar INICIO y FIN.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from django.utils import timezone

SANTIAGO = ZoneInfo("America/Santiago")

# Desde el 16-11-2026 00:00 hasta el 26-12-2026 23:59:59 (hora de Chile).
# FIN es EXCLUSIVO: el 27-12 a las 00:00 ya no se ve.
INICIO = datetime(2026, 11, 16, 0, 0, tzinfo=SANTIAGO)
FIN = datetime(2026, 12, 27, 0, 0, tzinfo=SANTIAGO)


def activa(ahora=None):
    """True si `ahora` (con zona horaria) cae dentro de la ventana."""
    ahora = ahora or timezone.now()
    return INICIO <= ahora < FIN


def contexto(request):
    return {"navidad_activa": activa()}
