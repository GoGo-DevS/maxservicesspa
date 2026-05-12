from django.db import models


class ContactRequest(models.Model):
    SERVICE_CLIMATIZATION = "climatizacion"
    SERVICE_AIR_CONDITIONING = "aire-acondicionado"
    SERVICE_VENTILATION = "ventilacion"
    SERVICE_EXTRACTION = "extraccion"
    SERVICE_PRESSURIZATION = "presurizacion"
    SERVICE_MAINTENANCE = "mantenciones"
    SERVICE_OTHER = "otro"

    SERVICE_CHOICES = [
        (SERVICE_CLIMATIZATION, "Climatización"),
        (SERVICE_AIR_CONDITIONING, "Aire acondicionado"),
        (SERVICE_VENTILATION, "Ventilación"),
        (SERVICE_EXTRACTION, "Extracción"),
        (SERVICE_PRESSURIZATION, "Presurización"),
        (SERVICE_MAINTENANCE, "Mantenciones"),
        (SERVICE_OTHER, "Otro requerimiento"),
    ]

    full_name = models.CharField("nombre", max_length=120)
    company = models.CharField("empresa o proyecto", max_length=140, blank=True)
    email = models.EmailField("correo electrónico")
    phone = models.CharField("teléfono", max_length=40, blank=True)
    service = models.CharField("servicio requerido", max_length=40, choices=SERVICE_CHOICES)
    location = models.CharField("ubicación", max_length=120, blank=True)
    message = models.TextField("detalle del requerimiento")
    created_at = models.DateTimeField("fecha de ingreso", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "solicitud de contacto"
        verbose_name_plural = "solicitudes de contacto"

    def __str__(self):
        company_suffix = f" | {self.company}" if self.company else ""
        return f"{self.full_name}{company_suffix}"
