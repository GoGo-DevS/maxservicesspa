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


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_EMAIL="contacto@maxservicesspa.cl",
    DEFAULT_FROM_EMAIL="contacto@maxservicesspa.cl",
)
class PaginasPropiasTests(TestCase):
    """Cada servicio con su propia URL (16-09-2026).

    Antes el sitio era UNA pagina y "Servicios", "Empresa" y "Contacto" eran
    anclas a la home: el sitemap publicaba 2 URLs y Google tenia una sola pagina
    indexada, asi que el sitio solo podia aparecer buscando su propia marca.
    """

    def test_todas_las_paginas_de_servicio_responden(self):
        from core.servicios import SERVICIOS

        for servicio in SERVICIOS:
            with self.subTest(servicio=servicio["slug"]):
                r = self.client.get(reverse("core:servicio", args=[servicio["slug"]]))
                self.assertEqual(r.status_code, 200)
                self.assertContains(r, servicio["h1"])

    def test_un_servicio_inventado_da_404(self):
        self.assertEqual(self.client.get("/servicios/no-existe/").status_code, 404)

    def test_cada_pagina_trae_su_propio_titulo_y_descripcion(self):
        """Repetir el title entre paginas es lo mismo que no tenerlo."""
        rutas = ["/", "/servicios/", "/empresa/", "/contacto/",
                 "/servicios/mantencion-hvac/", "/servicios/extraccion-de-aire/"]
        titulos, descripciones = set(), set()
        for ruta in rutas:
            html = self.client.get(ruta).content.decode()
            titulo = html.split("<title>")[1].split("</title>")[0]
            desc = html.split('name="description" content="')[1].split('"')[0]
            self.assertLessEqual(len(titulo), 70, f"title muy largo en {ruta}")
            self.assertTrue(desc.strip(), f"sin description en {ruta}")
            titulos.add(titulo)
            descripciones.add(desc)
        self.assertEqual(len(titulos), len(rutas), "hay titles repetidos entre paginas")
        self.assertEqual(len(descripciones), len(rutas), "hay descriptions repetidas")

    def test_el_canonical_apunta_a_la_misma_pagina(self):
        html = self.client.get("/servicios/mantencion-hvac/").content.decode()
        self.assertIn("/servicios/mantencion-hvac/\">", html.split('rel="canonical" href="')[1][:200])

    def test_la_pagina_de_servicio_declara_service_breadcrumb_y_faq(self):
        html = self.client.get("/servicios/mantencion-hvac/").content.decode()
        bloques = [json.loads(t.split("</script>")[0]) for t in
                   html.split('<script type="application/ld+json">')[1:]]
        tipos = set()
        for b in bloques:
            tipos.add(b.get("@type"))
            for sub in b.get("@graph", []):
                tipos.add(sub.get("@type"))
        self.assertTrue({"Service", "BreadcrumbList", "FAQPage"} <= tipos, tipos)

    def test_las_preguntas_del_schema_estan_escritas_en_la_pagina(self):
        """Marcar preguntas que el visitante no ve es lo que Google penaliza."""
        from core.servicios import POR_SLUG

        html = self.client.get("/servicios/mantencion-hvac/").content.decode()
        for item in POR_SLUG["mantencion-hvac"]["faq"]:
            self.assertIn(item["p"], html)

    def test_el_sitemap_publica_todas_las_paginas(self):
        """Publicaba 2 URLs: la home y /proyectos/."""
        from core.servicios import SERVICIOS
        from portfolio.catalog import get_project_catalog

        proyectos = get_project_catalog()["projects"]
        cuerpo = self.client.get("/sitemap.xml").content.decode()
        # home + indice de servicios + proyectos + empresa + contacto = 5 fijas
        self.assertEqual(cuerpo.count("<loc>"), 5 + len(SERVICIOS) + len(proyectos))
        for servicio in SERVICIOS:
            self.assertIn(f"/servicios/{servicio['slug']}/", cuerpo)
        for proyecto in proyectos:
            self.assertIn(f"/proyectos/{proyecto['slug']}/", cuerpo)

    def test_el_menu_lleva_a_las_paginas_y_no_a_anclas(self):
        html = self.client.get("/").content.decode()
        for ruta in ("/servicios/", "/empresa/", "/contacto/"):
            self.assertIn(f'href="{ruta}"', html, f"el menu no enlaza {ruta}")

    def test_la_home_enlaza_cada_tarjeta_con_su_servicio(self):
        """Es lo que le pasa autoridad a las paginas nuevas."""
        from core.servicios import SERVICIOS

        html = self.client.get("/").content.decode()
        for servicio in SERVICIOS:
            self.assertIn(f"/servicios/{servicio['slug']}/", html)

    def test_el_formulario_funciona_en_contacto_y_vuelve_a_contacto(self):
        datos = {
            "full_name": "Ana Rivas",
            "email": "ana@empresa.cl",
            "phone": "+56 9 1111 2222",
            "company": "Empresa Ejemplo",
            "service": "mantenciones",
            "region": "Metropolitana de Santiago",
            "city": "Santiago",
            "commune": "Providencia",
            "message": "Necesitamos un plan de mantención para 12 equipos de oficina.",
        }
        r = self.client.post("/contacto/", datos)
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r["Location"].startswith("/contacto/"), r["Location"])
        self.assertEqual(ContactRequest.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)


class SeguridadTests(TestCase):
    """DEBUG estaba en True Y ASI CORRIA EN PRODUCCION (16-09-2026).

    Se comprobo en vivo: https://maxservicesspa.cl/pagina-que-no-existe/ devolvia
    la pagina de depuracion de Django con el listado de rutas. Con un error 500
    habria mostrado la traza completa y las variables de entorno.
    """

    def test_debug_apagado_por_defecto(self):
        import importlib
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DJANGO_DEBUG", None)
            from config import settings as s
            importlib.reload(s)
            self.assertFalse(s.DEBUG, "DEBUG tiene que estar apagado si nadie lo pide")
            self.assertTrue(s.SECURE_SSL_REDIRECT)
            self.assertTrue(s.SESSION_COOKIE_SECURE)
            self.assertEqual(s.X_FRAME_OPTIONS, "DENY")
            self.assertNotIn("*", s.ALLOWED_HOSTS, "ALLOWED_HOSTS no puede ser comodin")
            self.assertIn("maxservicesspa.cl", s.ALLOWED_HOSTS)

    def test_la_clave_de_firma_sale_del_entorno(self):
        import importlib
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {"DJANGO_SECRET_KEY": "una-clave-larga-de-prueba-para-el-test"}):
            from config import settings as s
            importlib.reload(s)
            self.assertEqual(s.SECRET_KEY, "una-clave-larga-de-prueba-para-el-test")
