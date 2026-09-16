"""Un solo dominio para el sitio.

https://maxservicesspa.onrender.com respondia 200 con el sitio completo, o sea
el mismo contenido vivia en dos direcciones. Para Google eso es contenido
duplicado y reparte entre las dos lo que deberia acumular una sola. El canonical
ayuda, pero una redireccion 301 lo resuelve de verdad y ademas evita que alguien
comparta el enlace de Render.
"""
from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class DominioCanonicoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        destino = settings.SITE_URL.rstrip("/")
        self.destino = destino
        self.host_final = destino.split("//", 1)[-1]

    def __call__(self, request):
        host = request.get_host().split(":")[0]
        if (
            not settings.DEBUG
            and host.endswith(".onrender.com")
            and self.host_final
            and not self.host_final.endswith(".onrender.com")
        ):
            return HttpResponsePermanentRedirect(f"{self.destino}{request.get_full_path()}")
        return self.get_response(request)
