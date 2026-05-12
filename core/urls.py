from django.urls import path

from .views import home, location_cities_api, location_communes_api

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("api/locations/cities/", location_cities_api, name="location_cities_api"),
    path("api/locations/communes/", location_communes_api, name="location_communes_api"),
]
