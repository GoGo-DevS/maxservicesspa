"""Da acceso al panel y manda por correo el enlace para que la persona elija
su clave. Nadie mas la ve: ni Diego, ni el chat, ni la consola.

    python manage.py panel_invitar fda@maxservicesspa.cl --nombre Felipe --responde
    python manage.py panel_invitar otra@persona.cl --nombre Diego
"""
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from cotizaciones.permisos import GRUPO_PANEL, GRUPO_RESPONDE


class Command(BaseCommand):
    help = "Crea (o actualiza) una cuenta del panel y le manda el enlace para elegir clave."

    def add_arguments(self, parser):
        parser.add_argument("correo")
        parser.add_argument("--nombre", default="")
        parser.add_argument("--responde", action="store_true",
                            help="Es quien responde las cotizaciones (Felipe): al abrir, marca Vista.")
        parser.add_argument("--sin-correo", action="store_true",
                            help="Solo crea la cuenta; no manda el enlace.")

    def handle(self, *args, **opts):
        direccion = opts["correo"].strip().lower()
        try:
            validate_email(direccion)
        except ValidationError:
            raise CommandError(f"Correo no valido: {direccion}")
        User = get_user_model()
        user, creado = User.objects.get_or_create(
            username=direccion, defaults={"email": direccion}
        )
        if opts["nombre"]:
            user.first_name = opts["nombre"][:150]
        user.email = direccion
        user.is_active = True
        if creado or not user.has_usable_password():
            # Clave al azar que nadie conoce: sin una clave "usable" Django no
            # deja usar el enlace de cambio de clave.
            user.set_password(secrets.token_urlsafe(32))
        user.save()
        grupo = GRUPO_RESPONDE if opts["responde"] else GRUPO_PANEL
        user.groups.add(Group.objects.get_or_create(name=grupo)[0])

        if opts["sin_correo"]:
            self.stdout.write(f"Cuenta {'creada' if creado else 'actualizada'}: {direccion} ({grupo}).")
            return
        enlace = settings.SITE_URL.rstrip("/") + reverse(
            "cotizaciones:clave_nueva",
            kwargs={
                "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            },
        )
        contexto = {
            "nombre": user.first_name or direccion,
            "enlace": enlace,
            "panel_url": settings.SITE_URL.rstrip("/") + reverse("cotizaciones:bandeja"),
        }
        correo = EmailMultiAlternatives(
            "Tu acceso al panel de cotizaciones de Max Services",
            render_to_string("cotizaciones/emails/invitacion.txt", contexto),
            settings.DEFAULT_FROM_EMAIL,
            [direccion],
        )
        correo.attach_alternative(
            render_to_string("cotizaciones/emails/invitacion.html", contexto), "text/html"
        )
        correo.send(fail_silently=False)
        self.stdout.write(
            f"Cuenta {'creada' if creado else 'actualizada'}: {direccion} ({grupo}). "
            "Enlace para elegir clave enviado por correo."
        )
