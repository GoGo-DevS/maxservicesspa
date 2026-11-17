"""Navidad 2026: la franja y la decoracion las decide el servidor por fecha.

Ventana: 16-11-2026 00:00 a 26-12-2026 23:59:59, hora de Chile. Fuera de ella
la pagina no puede traer NADA de Navidad (ni el saludo, ni la hoja de estilos,
ni el script): se apaga sola, sin otro despliegue.
"""
from datetime import datetime, timezone as dt_timezone
from unittest.mock import patch

from django.test import TestCase, override_settings

from core import navidad

SANTIAGO = navidad.SANTIAGO
SALUDO = "les desea MAX Services"


def chile(*partes):
    return datetime(*partes, tzinfo=SANTIAGO)


class VentanaTests(TestCase):
    def test_bordes_de_la_ventana(self):
        casos = [
            (chile(2026, 11, 15, 12, 0), False),
            (chile(2026, 11, 15, 23, 59, 59), False),
            (chile(2026, 11, 16, 0, 0), True),
            (chile(2026, 12, 1, 12, 0), True),
            (chile(2026, 12, 26, 23, 59, 59), True),
            (chile(2026, 12, 27, 0, 0), False),
            (chile(2026, 12, 27, 12, 0), False),
            (chile(2027, 11, 20, 12, 0), False),
        ]
        for cuando, esperado in casos:
            with self.subTest(cuando=cuando.isoformat()):
                self.assertIs(navidad.activa(cuando), esperado)

    def test_la_hora_que_manda_es_la_de_chile_no_la_utc(self):
        # 16-11 a las 02:59 UTC todavia es 15-11 en Chile (UTC-3).
        self.assertFalse(navidad.activa(datetime(2026, 11, 16, 2, 59, tzinfo=dt_timezone.utc)))
        self.assertTrue(navidad.activa(datetime(2026, 11, 16, 3, 0, tzinfo=dt_timezone.utc)))
        # 27-12 a las 02:59 UTC todavia es 26-12 en Chile.
        self.assertTrue(navidad.activa(datetime(2026, 12, 27, 2, 59, tzinfo=dt_timezone.utc)))
        self.assertFalse(navidad.activa(datetime(2026, 12, 27, 3, 0, tzinfo=dt_timezone.utc)))


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PaginaConYSinNavidadTests(TestCase):
    RUTAS = ["/", "/servicios/", "/proyectos/", "/empresa/", "/contacto/"]

    def pedir(self, ruta, cuando):
        with patch("core.navidad.timezone.now", return_value=cuando):
            return self.client.get(ruta)

    def test_dentro_de_la_ventana_trae_saludo_guirnalda_estilos_y_script(self):
        for cuando in (chile(2026, 11, 16, 0, 0), chile(2026, 12, 26, 23, 59, 59)):
            for ruta in self.RUTAS:
                with self.subTest(ruta=ruta, cuando=cuando.isoformat()):
                    r = self.pedir(ruta, cuando)
                    self.assertEqual(r.status_code, 200)
                    html = r.content.decode()
                    self.assertIn("¡Felices Fiestas!", html)
                    self.assertIn(SALUDO, html)
                    self.assertIn('class="tema-navidad"', html)
                    self.assertIn("navidad-guirnalda", html)
                    # Las ramas (con su sombra) van en su propia capa quieta:
                    # sin ella, navidad.css no tiene donde dibujar la guirnalda.
                    self.assertIn('class="navidad-guirnalda__ramas"', html)
                    self.assertIn("css/navidad", html)
                    self.assertIn("js/navidad", html)

    def test_fuera_de_la_ventana_no_trae_nada_de_navidad(self):
        for cuando in (chile(2026, 11, 15, 23, 59, 59), chile(2026, 12, 27, 0, 0)):
            for ruta in self.RUTAS:
                with self.subTest(ruta=ruta, cuando=cuando.isoformat()):
                    r = self.pedir(ruta, cuando)
                    self.assertEqual(r.status_code, 200)
                    html = r.content.decode()
                    self.assertNotIn("Felices Fiestas", html)
                    self.assertNotIn("tema-navidad", html)
                    self.assertNotIn("navidad-guirnalda", html)
                    self.assertNotIn("css/navidad", html)
                    self.assertNotIn("js/navidad", html)

    def test_fuera_de_la_ventana_vuelve_el_texto_normal_de_la_franja(self):
        r = self.pedir("/", chile(2026, 12, 27, 0, 0))
        self.assertContains(r, "Santiago y Región Metropolitana | HVAC y mantenciones")
        r = self.pedir("/", chile(2026, 12, 1, 12, 0))
        self.assertNotContains(r, "Santiago y Región Metropolitana | HVAC y mantenciones")

    def test_el_saludo_no_ofrece_nada(self):
        # Es un saludo, no una campana: ni precios ni ofertas en la franja.
        html = self.pedir("/", chile(2026, 12, 1, 12, 0)).content.decode()
        inicio = html.index("navidad-saludo")
        franja = html[inicio:html.index("</p>", inicio)].lower()
        for palabra in ("$", "uf", "descuento", "oferta", "%", "gratis", "precio"):
            self.assertNotIn(palabra, franja)
