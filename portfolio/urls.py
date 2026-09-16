from django.urls import path

from .views import project_detail, projects_index

app_name = "portfolio"

urlpatterns = [
    path("", projects_index, name="projects_index"),
    # Ficha propia por proyecto (16-09-2026): antes las 16 fichas se dibujaban
    # con JavaScript dentro de /proyectos/ y para Google eran UNA sola pagina.
    path("<slug:slug>/", project_detail, name="project_detail"),
]
