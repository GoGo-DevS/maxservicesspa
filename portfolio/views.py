from django.http import Http404
from django.shortcuts import render

from core.seo import ID_EMPRESA, absolute_static_url, migas, schema_json, url_absoluta
from core.servicios import servicios_del_proyecto

from .catalog import get_project_catalog


def projects_index(request):
    return render(
        request,
        "portfolio/projects.html",
        {
            "current_page": "projects",
            "page_title": "Proyectos de climatización y ventilación | Max Services",
            "page_description": (
                "Obras de climatización, ventilación, extracción y presurización de Max Services "
                "SpA para TASCO Boetsch, Echeverría Izquierdo, salud y universidades."
            ),
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
    titulo = _titulo(proyecto)
    servicios = servicios_del_proyecto(proyecto)
    ficha = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": proyecto["name"],
        "headline": proyecto.get("titulo_seo") or proyecto["name"],
        "description": _descripcion(proyecto),
        "url": url_absoluta(ruta),
        "locationCreated": {"@type": "Place", "name": proyecto.get("location", "Santiago, Chile")},
        "about": [s["nombre"] for s in servicios] or proyecto.get("services", []),
        "creator": {"@type": "HVACBusiness", "@id": ID_EMPRESA, "name": "MAX SERVICES SpA"},
    }
    return render(
        request,
        "portfolio/project_detail.html",
        {
            "current_page": "projects",
            "page_title": titulo,
            "page_description": _descripcion(proyecto),
            "canonical_path": ruta,
            "og_image": absolute_static_url("assets/social/og-proyectos.jpg"),
            "proyecto": proyecto,
            "otros": _relacionados(proyecto, catalogo["projects"]),
            "servicios": servicios,
            "migas_visibles": camino,
            "schema_json": schema_json(ficha, migas(camino)),
        },
    )


MARCA = " | Max Services"


def _titulo(proyecto):
    """Title de la ficha, entero dentro de los ~60 caracteres que muestra Google.

    07-10-2026: los titles se armaban con el nombre completo + "Proyecto HVAC" +
    la marca y varios pasaban de 70: Google los cortaba justo en lo que
    distinguia una ficha de otra. Ahora cada proyecto trae su `titulo_seo`.
    """
    corto = proyecto.get("titulo_seo") or proyecto["name"]
    titulo = f"{corto}{MARCA}"
    if len(titulo) > 60:
        titulo = f"{corto[:60 - len(MARCA) - 1].rstrip()}…{MARCA}"
    return titulo


def _descripcion(proyecto):
    """Description que no se corta a media palabra."""
    texto = proyecto.get("descripcion_seo") or proyecto.get("summary", "")
    if len(texto) <= 155:
        return texto
    return texto[:154].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def _relacionados(proyecto, proyectos, cantidad=3):
    """Los proyectos que comparten mas especialidades con este.

    Antes eran siempre los tres primeros del catalogo: las 16 fichas enlazaban a
    las mismas tres y el resto no recibia ningun enlace desde otra ficha.
    """
    propios = set(proyecto.get("services", []))
    candidatos = [p for p in proyectos if p["slug"] != proyecto["slug"]]
    candidatos.sort(key=lambda p: -len(propios & set(p.get("services", []))))
    return candidatos[:cantidad]
