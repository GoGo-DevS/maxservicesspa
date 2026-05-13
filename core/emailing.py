import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from core.seo import absolute_static_url


logger = logging.getLogger(__name__)

SERVICE_LABELS = {
    "climatizacion": "Climatizacion",
    "aire-acondicionado": "Aire acondicionado",
    "ventilacion": "Ventilacion",
    "extraccion": "Extraccion",
    "presurizacion": "Presurizacion",
    "mantenciones": "Mantenciones",
    "otro": "Otro requerimiento",
}


def _build_contact_context(contact_request):
    return {
        "contact_request": contact_request,
        "service_label": SERVICE_LABELS.get(contact_request.service, contact_request.service),
        "phone_value": contact_request.phone or "No informado",
        "company_value": contact_request.company or "No informado",
        "location_value": contact_request.location or "No informado",
        "brand_logo_url": absolute_static_url("assets/brand/max-services-symbol-real-v2.png"),
    }


def _send_html_email(*, subject, to, html_template, text_template, context, reply_to=None):
    text_body = render_to_string(text_template, context)
    html_body = render_to_string(html_template, context)
    message = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        to,
        reply_to=reply_to or [],
    )
    message.attach_alternative(html_body, "text/html")
    try:
        message.send(fail_silently=False)
    except Exception as exc:
        print("SMTP DEBUG START", flush=True)
        print(f"exception_type={exc.__class__.__name__}", flush=True)
        print(f"exception_message={exc}", flush=True)
        print(f"EMAIL_HOST={settings.EMAIL_HOST}", flush=True)
        print(f"EMAIL_PORT={settings.EMAIL_PORT}", flush=True)
        print(f"EMAIL_USE_TLS={settings.EMAIL_USE_TLS}", flush=True)
        print(f"EMAIL_USE_SSL={settings.EMAIL_USE_SSL}", flush=True)
        print(f"EMAIL_HOST_USER={settings.EMAIL_HOST_USER}", flush=True)
        print(f"DEFAULT_FROM_EMAIL={settings.DEFAULT_FROM_EMAIL}", flush=True)
        print(f"CONTACT_EMAIL={settings.CONTACT_EMAIL}", flush=True)
        print(
            f"EMAIL_HOST_PASSWORD presente={'Sí' if settings.EMAIL_HOST_PASSWORD else 'No'}",
            flush=True,
        )
        logger.exception(
            "Email send failed. exception_type=%s exception_message=%s password_present=%s",
            exc.__class__.__name__,
            str(exc),
            bool(settings.EMAIL_HOST_PASSWORD),
        )
        raise


def send_contact_request_notification(contact_request):
    context = _build_contact_context(contact_request)

    _send_html_email(
        subject="Nueva consulta desde la web MAX SERVICES SPA",
        to=[settings.CONTACT_EMAIL],
        html_template="emails/contact_internal.html",
        text_template="emails/contact_internal.txt",
        context=context,
        reply_to=[contact_request.email],
    )

    _send_html_email(
        subject="Hemos recibido tu solicitud | MAX SERVICES SPA",
        to=[contact_request.email],
        html_template="emails/contact_customer_confirmation.html",
        text_template="emails/contact_customer_confirmation.txt",
        context=context,
    )
