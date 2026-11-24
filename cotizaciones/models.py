"""Panel de cotizaciones de Max Services (23-11-2026).

Hasta esta fecha las cotizaciones llegaban a contacto@maxservicesspa.cl, Diego
las reenviaba a mano a Felipe (fda@) y nadie sabia despues si alguien habia
contestado. Entre el 20-10 y el 23-11 llegaron unas 17 solicitudes reales y
desde contacto@ no salio ninguna respuesta: GITPRO tuvo que volver a escribir
con "URGENTE" cinco dias despues de pedir su cotizacion.

El panel junta en una bandeja las consultas del formulario y los correos que
llegan a contacto@, y deja registrado quien vio cada una, cuando se respondio y
en que etapa va.

Regla de diseno: el correo es la fuente de verdad. Si esta base se pierde (el
sitio corre con SQLite), una sincronizacion vuelve a armar las solicitudes y a
detectar cuales se respondieron. Lo unico que no se recupera es lo que se marco
a mano (etapas, notas).
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class Solicitud(models.Model):
    class Origen(models.TextChoices):
        WEB = "web", "Formulario web"
        CORREO = "correo", "Correo"

    class Categoria(models.TextChoices):
        COTIZACION = "cotizacion", "Cotización"
        DUDOSO = "dudoso", "Por revisar"
        OTRO = "otro", "No es cotización"

    class Estado(models.TextChoices):
        NUEVA = "nueva", "Nueva"
        VISTA = "vista", "Vista"
        RESPONDIDA = "respondida", "Respondida"
        COTIZADA = "cotizada", "Cotizada"
        GANADA = "ganada", "Ganada"
        PERDIDA = "perdida", "Perdida"

    ESTADOS_ABIERTOS = (Estado.NUEVA, Estado.VISTA)
    ESTADOS_CERRADOS = (Estado.GANADA, Estado.PERDIDA)

    origen = models.CharField(max_length=10, choices=Origen.choices)
    categoria = models.CharField(
        max_length=12, choices=Categoria.choices, default=Categoria.COTIZACION
    )
    estado = models.CharField(
        max_length=12, choices=Estado.choices, default=Estado.NUEVA, db_index=True
    )

    cliente_nombre = models.CharField("nombre", max_length=160, blank=True)
    cliente_email = models.CharField("correo", max_length=254, db_index=True)
    cliente_empresa = models.CharField("empresa o proyecto", max_length=160, blank=True)
    cliente_telefono = models.CharField("teléfono", max_length=40, blank=True)
    servicio = models.CharField(max_length=80, blank=True)
    ubicacion = models.CharField("ubicación", max_length=160, blank=True)
    asunto = models.CharField(max_length=300, blank=True)
    detalle = models.TextField(blank=True)

    recibida_en = models.DateTimeField(db_index=True)
    # Hilo de Gmail (X-GM-THRID, en decimal). Sirve para el enlace "abrir en
    # Gmail" y para colgar las respuestas del mismo hilo.
    gmail_hilo = models.CharField(max_length=32, blank=True, db_index=True)
    contact_request = models.OneToOneField(
        "core.ContactRequest",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="solicitud_panel",
    )

    # Desde cuando el cliente espera respuesta. None = no espera nada (el
    # ultimo mensaje real del hilo es nuestro). Es lo que mira el aviso.
    esperando_desde = models.DateTimeField(null=True, blank=True, db_index=True)

    vista_en = models.DateTimeField(null=True, blank=True)
    vista_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    respondida_en = models.DateTimeField(null=True, blank=True)
    respondida_por = models.CharField(max_length=254, blank=True)
    ultimo_aviso_en = models.DateTimeField(null=True, blank=True)
    # Ultima vez que el cliente escribio. Decide que solicitudes se muestran
    # (PANEL_DESDE) y ordena las respondidas: un hilo viejo que el cliente
    # reactiva esta semana tiene que aparecer.
    actividad_en = models.DateTimeField(null=True, blank=True, db_index=True)

    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recibida_en"]
        verbose_name = "solicitud"
        verbose_name_plural = "solicitudes"
        indexes = [models.Index(fields=["categoria", "estado"])]

    def __str__(self):
        quien = self.cliente_empresa or self.cliente_nombre or self.cliente_email
        return f"{quien} | {self.asunto or self.get_origen_display()}"

    @property
    def cerrada(self):
        return self.estado in self.ESTADOS_CERRADOS

    @property
    def titulo(self):
        return self.cliente_empresa or self.cliente_nombre or self.cliente_email

    def registrar(self, tipo, detalle="", usuario=None):
        return Evento.objects.create(
            solicitud=self, tipo=tipo, detalle=detalle[:300], usuario=usuario
        )

    def marcar_respondida(self, fecha, por, usuario=None, detalle=""):
        """Se llama cuando sale una respuesta real al cliente (o Felipe la marca
        a mano). Nunca retrocede una etapa: una solicitud Cotizada sigue
        Cotizada aunque llegue otra respuesta."""
        cambios = []
        if self.respondida_en is None:
            self.respondida_en = fecha
            self.respondida_por = por[:254]
            cambios += ["respondida_en", "respondida_por"]
        if self.esperando_desde is not None and fecha >= self.esperando_desde:
            self.esperando_desde = None
            cambios.append("esperando_desde")
        if self.estado in self.ESTADOS_ABIERTOS:
            self.estado = self.Estado.RESPONDIDA
            cambios.append("estado")
        if cambios:
            self.save(update_fields=cambios + ["actualizada_en"])
            self.registrar(
                Evento.Tipo.RESPONDIDA, detalle or f"Respondida por {por}", usuario
            )
        return bool(cambios)


class Mensaje(models.Model):
    class Sentido(models.TextChoices):
        ENTRANTE = "entrante", "Del cliente"
        SALIENTE = "saliente", "Respuesta de Max"
        INTERNO = "interno", "Reenvío interno"

    solicitud = models.ForeignKey(
        Solicitud, on_delete=models.CASCADE, related_name="mensajes"
    )
    message_id = models.CharField(max_length=300, unique=True)
    sentido = models.CharField(max_length=10, choices=Sentido.choices)
    # Autorespuesta "Hemos recibido tu solicitud": va al cliente pero no le
    # contesta nada, asi que no cuenta como respuesta.
    automatico = models.BooleanField(default=False)
    de = models.CharField(max_length=254)
    de_nombre = models.CharField(max_length=160, blank=True)
    para = models.TextField(blank=True)
    cc = models.TextField(blank=True)
    asunto = models.CharField(max_length=300, blank=True)
    extracto = models.TextField(blank=True)
    adjuntos = models.JSONField(default=list, blank=True)
    fecha = models.DateTimeField(db_index=True)
    gmail_hilo = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ["fecha", "pk"]
        verbose_name = "mensaje"
        verbose_name_plural = "mensajes"

    def __str__(self):
        return f"{self.get_sentido_display()} {self.fecha:%d-%m %H:%M} {self.asunto}"


class Evento(models.Model):
    class Tipo(models.TextChoices):
        CREADA = "creada", "Llegó"
        VISTA = "vista", "Vista"
        RESPONDIDA = "respondida", "Respondida"
        ESTADO = "estado", "Cambio de etapa"
        CATEGORIA = "categoria", "Clasificación"
        NOTA = "nota", "Nota"
        AVISO = "aviso", "Aviso enviado"
        CLIENTE = "cliente", "El cliente escribió"
        REENVIO = "reenvio", "Reenvío interno"

    solicitud = models.ForeignKey(
        Solicitud, on_delete=models.CASCADE, related_name="eventos"
    )
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    detalle = models.CharField(max_length=300, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["creado_en", "pk"]
        verbose_name = "evento"
        verbose_name_plural = "eventos"

    def __str__(self):
        return f"{self.get_tipo_display()} {self.creado_en:%d-%m %H:%M}"


class Sincronizacion(models.Model):
    """Una sola fila: hasta que UID de la casilla ya se leyo y cuando salio el
    ultimo aviso. Si la base se pierde, se vuelve a leer desde cero."""

    carpeta = models.CharField(max_length=120, blank=True)
    uidvalidity = models.BigIntegerField(null=True, blank=True)
    ultimo_uid = models.BigIntegerField(default=0)
    ultima_corrida = models.DateTimeField(null=True, blank=True)
    ultimo_error = models.TextField(blank=True)
    ultimo_aviso_turno = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "sincronización"
        verbose_name_plural = "sincronización"

    @classmethod
    def actual(cls):
        fila, _ = cls.objects.get_or_create(pk=1)
        return fila
