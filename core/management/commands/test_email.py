from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Send a test email using the configured SMTP settings."

    def handle(self, *args, **options):
        self.stdout.write("SMTP settings:")
        self.stdout.write(f"EMAIL_HOST={settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL_PORT={settings.EMAIL_PORT}")
        self.stdout.write(f"EMAIL_USE_TLS={settings.EMAIL_USE_TLS}")
        self.stdout.write(f"EMAIL_HOST_USER={settings.EMAIL_HOST_USER}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL={settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"CONTACT_EMAIL={settings.CONTACT_EMAIL}")
        self.stdout.write(
            f"EMAIL_HOST_PASSWORD presente={'Sí' if settings.EMAIL_HOST_PASSWORD else 'No'}"
        )

        try:
            sent_count = send_mail(
                subject="Prueba SMTP MAX SERVICES SPA",
                message=(
                    "Este es un correo de prueba enviado desde el comando "
                    "python manage.py test_email."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
        except Exception as exc:
            self.stderr.write("SMTP test failed.")
            self.stderr.write(f"exception_type={exc.__class__.__name__}")
            self.stderr.write(f"exception_message={exc}")
            self.stderr.write(
                f"EMAIL_HOST_PASSWORD presente={'Sí' if settings.EMAIL_HOST_PASSWORD else 'No'}"
            )
            raise CommandError("No se pudo enviar el correo de prueba.") from exc

        self.stdout.write(self.style.SUCCESS(f"Correo de prueba enviado. sent_count={sent_count}"))
