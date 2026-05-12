from django.urls import path

from .views import projects_index

app_name = "portfolio"

urlpatterns = [
    path("", projects_index, name="projects_index"),
]
