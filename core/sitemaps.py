from django.contrib.sitemaps import Sitemap

from core.servicios import SERVICIOS
from portfolio.catalog import get_project_catalog


class StaticViewSitemap(Sitemap):
    """Todas las URLs del sitio, no solo dos.

    Hasta el 16-09-2026 publicaba "/" y "/proyectos/" nada mas, porque el resto
    del sitio eran anclas. Con las paginas de servicio, empresa y contacto, el
    sitemap pasa a tener 10 URLs reales.
    """

    changefreq = "weekly"
    priority = 0.8

    def priority(self, item):  # noqa: F811
        if item == "/":
            return 1.0
        if item.startswith("/servicios/"):
            return 0.9
        if item.startswith("/proyectos/") and item != "/proyectos/":
            return 0.6
        return 0.8

    def items(self):
        return [
            "/",
            "/servicios/",
            *[f"/servicios/{s['slug']}/" for s in SERVICIOS],
            "/proyectos/",
            *[f"/proyectos/{p['slug']}/" for p in get_project_catalog()["projects"]],
            "/empresa/",
            "/contacto/",
        ]

    def location(self, item):
        return item

    def priority_for(self, item):
        return self.priority
