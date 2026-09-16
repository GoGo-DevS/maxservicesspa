from django.http import Http404
from django.shortcuts import render

from core.seo import absolute_static_url, migas, schema_json, url_absoluta
from core.servicios import SERVICIOS

from .catalog import get_project_catalog


def projects_index(request):
    return render(
        request,
        "portfolio/projects.html",
        {
            "current_page": "projects",
            "page_title": "Proyectos HVAC y climatización | MAX SERVICES SPA",
            "page_description": "Conoce la experiencia de MAX SERVICES SPA en climatización, ventilación, extracción, mantención y proyectos técnicos para distintos rubros.",
            "canonical_path": "/proyectos/",
            "og_image": absolute_static_url("assets/social/og-proyectos.jpg"),
            "project_catalog": get_project_catalog(),
            "proyectos": get_project_catalog()["projects"],
            "migas_visibles": [("Inicio", "/"), ("Proyectos", "/proyectos/")],
            "schema_json": schema_json(migas([("Inicio", "/"), ("Proyectos", "/proyectos/")])),
        },
    )


def project_detail(request, slug):
    """Ficha de un proyecto, con su propia URL."""
    catalogo = get_project_catalog()
    proyecto = next((p for p in catalogo["projects"] if p["slug"] == slug), None)
    if proyecto is None:
        raise Http404("Proyecto no encontrado")

    ruta = f"/proyectos/{slug}/"
    camino = [("Inicio", "/"), ("Proyectos", "/proyectos/"), (proyecto["name"], ruta)]
    titulo = f"{proyecto['name']} | Proyecto HVAC | MAX SERVICES"
    ficha = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": proyecto["name"],
        "description": proyecto.get("summary", ""),
        "url": url_absoluta(ruta),
        "locationCreated": {"@type": "Place", "name": proyecto.get("location", "Santiago, Chile")},
        "creator": {"@type": "Organization", "name": "MAX SERVICES SPA", "url": url_absoluta("/")},
    }
    return render(
        request,
        "portfolio/project_detail.html",
        {
            "current_page": "projects",
            # El title se corta en ~60 caracteres en Google: si el nombre del
            # proyecto ya es largo, se deja solo con la marca corta.
            "page_title": titulo if len(titulo) <= 70 else f"{proyecto['name']} | MAX SERVICES",
            "page_description": proyecto.get("summary", "")[:155],
            "canonical_path": ruta,
            "og_image": absolute_static_url("assets/social/og-proyectos.jpg"),
            "proyecto": proyecto,
            "otros": [p for p in catalogo["projects"] if p["slug"] != slug][:3],
            "servicios": SERVICIOS,
            "migas_visibles": camino,
            "schema_json": schema_json(ficha, migas(camino)),
        },
    )
