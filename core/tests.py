from unittest.mock import patch
import json

from django.core import mail
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from core.models import ContactRequest


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_EMAIL="contacto@maxservicesspa.cl",
    DEFAULT_FROM_EMAIL="contacto@maxservicesspa.cl",
)
class HomeViewTests(TestCase):
    def test_home_responds_successfully(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")

    def test_location_cities_api_returns_results(self):
        response = self.client.get(
            reverse("core:location_cities_api"),
            {"region": "Metropolitana de Santiago"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Santiago")

    def test_location_communes_api_returns_city_specific_results(self):
        response = self.client.get(
            reverse("core:location_communes_api"),
            {"region": "Valparaiso", "city": "Valparaiso"},
        )

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        labels = [item["label"] for item in payload["results"]]
        self.assertIn("Vina del Mar", labels)

    def test_valid_contact_form_creates_request_and_redirects(self):
        response = self.client.post(
            reverse("core:home"),
            data={
                "full_name": "Diego Pérez",
                "company": "Edificio Apoquindo",
                "email": "diego@example.com",
                "phone": "+56 9 1234 5678",
                "service": "mantenciones",
                "region": "Metropolitana de Santiago",
                "city": "Santiago",
                "commune": "Las Condes",
                "message": "Necesito evaluación para mantención preventiva del sistema central.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("core:home")))
        self.assertEqual(ContactRequest.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)

        internal_mail = mail.outbox[0]
        customer_mail = mail.outbox[1]

        self.assertEqual(internal_mail.to, ["contacto@maxservicesspa.cl"])
        self.assertEqual(internal_mail.reply_to, ["diego@example.com"])
        self.assertEqual(internal_mail.subject, "Nueva consulta desde la web MAX SERVICES SPA")
        self.assertEqual(customer_mail.to, ["diego@example.com"])
        self.assertEqual(customer_mail.reply_to, [])
        self.assertEqual(customer_mail.subject, "Hemos recibido tu solicitud | MAX SERVICES SPA")
        self.assertIn("Diego Pérez", customer_mail.body)
        self.assertIn("Mantenciones", customer_mail.body)

    def test_invalid_contact_form_does_not_create_request(self):
        response = self.client.post(
            reverse("core:home"),
            data={
                "full_name": "",
                "company": "Edificio Apoquindo",
                "email": "",
                "phone": "+56 9 1234 5678",
                "service": "mantenciones",
                "region": "Metropolitana de Santiago",
                "city": "Santiago",
                "commune": "Las Condes",
                "message": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactRequest.objects.count(), 0)
        self.assertContains(response, "Completa los datos marcados")
        self.assertEqual(len(mail.outbox), 0)

    def test_phone_city_commune_and_message_are_required(self):
        response = self.client.post(
            reverse("core:home"),
            data={
                "full_name": "Diego Pérez",
                "company": "Edificio Apoquindo",
                "email": "diego@example.com",
                "phone": "",
                "service": "mantenciones",
                "region": "",
                "city": "",
                "commune": "",
                "message": "Muy corto",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ingresa un teléfono de contacto.")
        self.assertContains(response, "Selecciona una región.")
        self.assertContains(response, "Selecciona una ciudad.")
        self.assertContains(response, "Entrega un poco más de detalle para poder evaluar el requerimiento.")
        self.assertEqual(ContactRequest.objects.count(), 0)

    def test_full_name_requires_name_and_surname(self):
        response = self.client.post(
            reverse("core:home"),
            data={
                "full_name": "Diego",
                "company": "Edificio Apoquindo",
                "email": "diego@example.com",
                "phone": "+56 9 1234 5678",
                "service": "mantenciones",
                "region": "Metropolitana de Santiago",
                "city": "Santiago",
                "commune": "Las Condes",
                "message": "Necesito evaluación para mantención preventiva del sistema central.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ingresa nombre y apellido completos.")
        self.assertEqual(ContactRequest.objects.count(), 0)

    def test_commune_must_match_selected_city(self):
        response = self.client.post(
            reverse("core:home"),
            data={
                "full_name": "Diego Pérez",
                "company": "Edificio Apoquindo",
                "email": "diego@example.com",
                "phone": "+56 9 1234 5678",
                "service": "mantenciones",
                "region": "Metropolitana de Santiago",
                "city": "Santiago",
                "commune": "Concon",
                "message": "Necesito evaluación para mantención preventiva del sistema central.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Selecciona una comuna válida para la ciudad indicada.")
        self.assertEqual(ContactRequest.objects.count(), 0)

    @patch("core.views.send_contact_request_notification", side_effect=OSError("smtp down"))
    def test_contact_form_keeps_record_when_email_fails(self, _mock_send):
        response = self.client.post(
            reverse("core:home"),
            data={
                "full_name": "Diego Pérez",
                "company": "Edificio Apoquindo",
                "email": "diego@example.com",
                "phone": "+56 9 1234 5678",
                "service": "mantenciones",
                "region": "Metropolitana de Santiago",
                "city": "Santiago",
                "commune": "Las Condes",
                "message": "Necesito evaluación para mantención preventiva del sistema central.",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactRequest.objects.count(), 1)
        self.assertContains(
            response,
            "La solicitud fue registrada correctamente, pero el aviso por correo no pudo enviarse en este momento.",
        )
