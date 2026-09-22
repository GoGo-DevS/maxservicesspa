"""El telefono que se lee, el que se marca y el que lee Google son el mismo.

22-09-2026: la web mostraba 22 559 01 08, pero el boton "Llamar" y el
JSON-LD usaban +56 2 2569 0108 desde la primera version. Quien apretaba
Llamar marcaba otro numero, y Google veia un telefono distinto al del
Perfil de Empresa. El numero correcto lo confirmo Diego con el cliente.
"""
import json
import re

from django.test import TestCase

CORRECTO = "+56225590108"


def solo_digitos(texto):
    return re.sub(r"\D", "", texto)


class UnSoloTelefono(TestCase):
    def setUp(self):
        self.html = self.client.get("/").content.decode()

    def test_el_boton_llamar_marca_el_numero_correcto(self):
        enlaces = set(re.findall(r'href="tel:([^"]+)"', self.html))
        self.assertTrue(enlaces)
        self.assertEqual(enlaces, {CORRECTO})

    def test_el_numero_visible_es_el_mismo_que_se_marca(self):
        self.assertIn("22 559 01 08", self.html)
        self.assertEqual("56" + solo_digitos("22 559 01 08"), CORRECTO.lstrip("+"))

    def test_google_lee_el_mismo_telefono(self):
        telefonos = set()
        for bloque in re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.html, re.S):
            telefonos |= set(re.findall(r'"telephone":\s*"([^"]+)"', bloque))
        self.assertEqual(telefonos, {CORRECTO})
