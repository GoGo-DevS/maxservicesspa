from django.contrib import admin

from .models import Evento, Mensaje, Sincronizacion, Solicitud


class MensajeEnLinea(admin.TabularInline):
    model = Mensaje
    extra = 0
    fields = ("fecha", "sentido", "automatico", "de", "asunto")
    readonly_fields = fields
    show_change_link = True


class EventoEnLinea(admin.TabularInline):
    model = Evento
    extra = 0
    fields = ("creado_en", "tipo", "detalle", "usuario")
    readonly_fields = fields


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ("recibida_en", "titulo", "asunto", "origen", "categoria", "estado", "esperando_desde")
    list_filter = ("estado", "categoria", "origen")
    search_fields = ("cliente_nombre", "cliente_email", "cliente_empresa", "asunto")
    inlines = [MensajeEnLinea, EventoEnLinea]
    raw_id_fields = ("contact_request",)
    readonly_fields = ("creada_en", "actualizada_en", "vista_en", "vista_por", "respondida_en", "respondida_por")


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ("fecha", "sentido", "de", "asunto", "solicitud")
    list_filter = ("sentido", "automatico")
    search_fields = ("de", "asunto", "message_id")
    raw_id_fields = ("solicitud",)


@admin.register(Sincronizacion)
class SincronizacionAdmin(admin.ModelAdmin):
    list_display = ("ultima_corrida", "carpeta", "ultimo_uid", "ultimo_aviso_turno", "ultimo_error")
