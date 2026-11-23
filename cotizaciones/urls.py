from django.urls import path

from . import views

app_name = "cotizaciones"

urlpatterns = [
    path("", views.bandeja, name="bandeja"),
    path("<int:pk>/", views.detalle, name="detalle"),
    path("<int:pk>/accion/", views.accion, name="accion"),
    path("adjunto/<int:pk>/<int:n>/", views.adjunto, name="adjunto"),
    path("sincronizar/", views.sincronizar_ahora, name="sincronizar"),
    path("tareas/correo/", views.tarea, name="tarea"),
    path("entrar/", views.Entrar.as_view(), name="entrar"),
    path("salir/", views.Salir.as_view(), name="salir"),
    path("clave/", views.PedirClave.as_view(), name="clave_pedir"),
    path("clave/enviada/", views.ClaveEnviada.as_view(), name="clave_enviada"),
    path("clave/<uidb64>/<token>/", views.NuevaClave.as_view(), name="clave_nueva"),
    path("clave/lista/", views.ClaveLista.as_view(), name="clave_lista"),
]
