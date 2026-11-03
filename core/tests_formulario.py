"""El formulario de cotizacion es la conversion del sitio (03-11-2026).

Las 5 cotizaciones de octubre llegaron por aca. Hasta esta fecha el formulario
de TODAS las paginas enviaba a la portada (`action="/#formulario"`): quien
cotizaba desde la pagina de presurizacion terminaba en la home, y si le faltaba
un dato veia el error en otra pagina. La prueba que existia posteaba directo a
/contacto/, asi que pasaba aunque el formulario real nunca llegara ahi.

Estas pruebas leen el `action` del HTML que ve la persona, no la URL que uno
cree que usa.
"""
import re

from django.core import mail
from django.test import TestCase, override_settings

from core.models import ContactRequest
from core.servicios import SERVICIOS

ACTION = re.compile(r'<form method="post" action="([^"]*)"')

DATOS_VALIDOS = {
    "full_name": "Ana Rivas",
    "email": "ana@empresa.cl",
    "phone": "+56 9 1111 2222",
    "company": "Edificio Ejemplo",
    "service": "presurizacion",
    "region": "Metropolitana de Santiago",
    "city": "Santiago",
    "commune": "Providencia",
    "message": "Necesitamos revisar el sistema de presurizacion de la escalera del edificio.",
}

PAGINAS_CON_FORMULARIO = ["/", "/contacto/"] + [f"/servicios/{s['slug']}/" for s in SERVICIOS]


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_EMAIL="contacto@maxservicesspa.cl",
    DEFAULT_FROM_EMAIL="contacto@maxservicesspa.cl",
)
class FormularioEnSuPropiaPaginaTests(TestCase):
    def test_cada_pagina_envia_el_formulario_a_si_misma(self):
        for ruta in PAGINAS_CON_FORMULARIO:
            with self.subTest(ruta=ruta):
                html = self.client.get(ruta).content.decode()
                acciones = ACTION.findall(html)
                self.assertEqual(acciones, [f"{ruta}#formulario"], ruta)

    def test_cotizar_desde_un_servicio_vuelve_al_mismo_servicio(self):
        ruta = "/servicios/presurizacion-de-escaleras/"
        r = self.client.post(ruta, DATOS_VALIDOS)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], f"{ruta}?focus=formulario#formulario")
        self.assertEqual(ContactRequest.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)
        # El mensaje de exito se ve en la pagina a la que vuelve.
        pagina = self.client.get(r["Location"]).content.decode()
        self.assertIn("Solicitud enviada correctamente", pagina)

    def test_un_error_se_muestra_en_el_mismo_servicio_y_no_guarda_nada(self):
        ruta = "/servicios/extraccion-cocinas-industriales/"
        datos = dict(DATOS_VALIDOS, phone="")
        r = self.client.post(ruta, datos)
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "core/servicio.html")
        self.assertContains(r, "Ingresa un teléfono de contacto.")
        # Lo que la persona ya escribio no se pierde.
        self.assertContains(r, "Edificio Ejemplo")
        self.assertEqual(ContactRequest.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_el_aviso_no_queda_debajo_de_la_cabecera_fija(self):
        """Fuera de la portada el navegador baja solo a #formulario y la cabecera
        fija (169 px) tapaba el aviso de error o de exito. Comprobado con Chromium
        contra el sitio local: sin esta regla el aviso quedaba en y=22."""
        from pathlib import Path

        from django.conf import settings

        css = (Path(settings.BASE_DIR) / "static/css/styles.css").read_text(encoding="utf-8")
        regla = re.search(r"#formulario\s*\{\s*scroll-margin-top:\s*(\d+)px", css)
        self.assertIsNotNone(regla)
        self.assertGreaterEqual(int(regla.group(1)), 170)

    def test_la_portada_sigue_recibiendo_su_formulario(self):
        r = self.client.post("/", DATOS_VALIDOS)
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r["Location"].startswith("/?focus=formulario"), r["Location"])
        self.assertEqual(ContactRequest.objects.count(), 1)


class ServicioPreseleccionadoTests(TestCase):
    """Quien cotiza desde la pagina de un servicio no tiene que volver a elegirlo,
    y Max recibe la solicitud ya clasificada."""

    ESPERADO = {
        "climatizacion-aire-acondicionado": "climatizacion",
        "ventilacion-inyeccion-de-aire": "ventilacion",
        "extraccion-de-aire": "extraccion",
        "extraccion-cocinas-industriales": "extraccion",
        "presurizacion-de-escaleras": "presurizacion",
        "mantencion-hvac": "mantenciones",
    }

    def _seleccionado(self, html):
        select = html.split('name="service"')[1].split("</select>")[0]
        # La opcion vacia ("---------") sale marcada cuando no hay nada elegido.
        return [v for v in re.findall(r'<option value="([^"]*)" selected>', select) if v]

    def test_cada_servicio_llega_con_su_opcion_elegida(self):
        for slug, valor in self.ESPERADO.items():
            with self.subTest(slug=slug):
                html = self.client.get(f"/servicios/{slug}/").content.decode()
                self.assertEqual(self._seleccionado(html), [valor])

    def test_reparacion_no_inventa_una_opcion(self):
        # No hay opcion "reparacion" en el formulario: se deja que la persona elija.
        html = self.client.get("/servicios/reparacion-de-sistemas/").content.decode()
        self.assertEqual(self._seleccionado(html), [])

    def test_portada_y_contacto_no_preseleccionan(self):
        for ruta in ["/", "/contacto/"]:
            with self.subTest(ruta=ruta):
                html = self.client.get(ruta).content.decode()
                self.assertEqual(self._seleccionado(html), [])

    def test_si_la_persona_cambia_la_opcion_manda_la_suya(self):
        r = self.client.post(
            "/servicios/presurizacion-de-escaleras/",
            dict(DATOS_VALIDOS, service="mantenciones"),
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(ContactRequest.objects.get().service, "mantenciones")
