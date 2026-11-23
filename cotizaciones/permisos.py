"""Quien entra al panel.

Iniciar sesion NO basta (criterio G-03): el sitio tiene /admin/ y cualquier
cuenta que exista ahi no tiene por que ver las cotizaciones. Entra quien esta
en uno de los dos grupos, o un superusuario.

- "Responde cotizaciones" (Felipe): cuando abre una solicitud, queda marcada
  como Vista. Es lo que Diego quiere poder ver.
- "Panel cotizaciones" (Diego u otros): ve todo, pero abrir no marca nada.
"""
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.urls import reverse

GRUPO_PANEL = "Panel cotizaciones"
GRUPO_RESPONDE = "Responde cotizaciones"


def _grupos(user):
    if not hasattr(user, "_grupos_panel"):
        user._grupos_panel = set(user.groups.values_list("name", flat=True))
    return user._grupos_panel


def puede_ver(user) -> bool:
    if not (user.is_authenticated and user.is_active):
        return False
    return user.is_superuser or bool(_grupos(user) & {GRUPO_PANEL, GRUPO_RESPONDE})


def responde(user) -> bool:
    return user.is_authenticated and GRUPO_RESPONDE in _grupos(user)


def sin_indexar(respuesta):
    respuesta["X-Robots-Tag"] = "noindex, nofollow"
    respuesta["Cache-Control"] = "private, no-store"
    return respuesta


def panel_requerido(vista):
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse("cotizaciones:entrar"))
        if not puede_ver(request.user):
            raise PermissionDenied("Esta cuenta no tiene acceso al panel de cotizaciones.")
        return sin_indexar(vista(request, *args, **kwargs))

    return envoltura
