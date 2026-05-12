from django.shortcuts import render

from .catalog import get_project_catalog


def projects_index(request):
    return render(
        request,
        "portfolio/projects.html",
        {
            "page_title": "Proyectos | MAX SERVICES SpA",
            "page_description": "Portafolio de referencias y proyectos ejecutados por MAX SERVICES SpA en retail, salud, universidades, oficinas, edificios y recintos técnicos desde 2011.",
            "project_catalog": get_project_catalog(),
        },
    )
