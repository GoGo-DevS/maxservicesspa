from django.urls import path

from .views import (
    contacto,
    empresa,
    home,
    location_cities_api,
    location_communes_api,
    servicio_detalle,
    servicios_index,
)

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    # Cada servicio con URL propia (16-09-2026). Antes eran anclas a la home:
    # sin URL propia no hay pagina que Google pueda mostrar por esa busqueda.
    path("servicios/", servicios_index, name="servicios"),
    path("servicios/<slug:slug>/", servicio_detalle, name="servicio"),
    path("empresa/", empresa, name="empresa"),
    path("contacto/", contacto, name="contacto"),
    path("api/locations/cities/", location_cities_api, name="location_cities_api"),
    path("api/locations/communes/", location_communes_api, name="location_communes_api"),
]
