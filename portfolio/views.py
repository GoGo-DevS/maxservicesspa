from django.shortcuts import render

from core.seo import absolute_static_url

from .catalog import get_project_catalog


def projects_index(request):
    return render(
        request,
        "portfolio/projects.html",
        {
            "page_title": "Proyectos HVAC y climatización | MAX SERVICES SPA",
            "page_description": "Conoce la experiencia de MAX SERVICES SPA en climatización, ventilación, extracción, mantención y proyectos técnicos para distintos rubros.",
            "canonical_path": "/proyectos/",
            "og_image": absolute_static_url("assets/projects/climatizacion-oficinas-las-condes/cover.png"),
            "project_catalog": get_project_catalog(),
        },
    )
