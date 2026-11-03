"""Tanda SEO del 03-11-2026: cada busqueda con demanda, a UNA pagina.

Linea base (Search Console 04-10 a 31-10): 16 clics, 782 impresiones, pos 8,3.
La demanda sale de Search Console y del autocompletado de Google (gl=cl), sin
volumenes inventados. Lo que estas pruebas cuidan:

- /servicios/extraccion-cocinas-industriales/ estaba "Descubierta: actualmente
  sin indexar": el 70 % de su texto ya estaba en /extraccion-de-aire/, cuyo H1
  tambien decia "cocinas", no tenia enlace desde la portada y el sitemap la
  fechaba antes de que existiera.
- "inyeccion de aire" y "extraccion e inyeccion de aire" (pos 3-9) caen en la
  pagina de ventilacion: el title y el H1 dicen esa frase.
- La pagina de mantencion apuntaba a una busqueda de casas (pos 48-53); ahora a
  la de empresas.
"""
import html as html_lib
import re
from datetime import date

from django.test import TestCase

from core.servicios import POR_SLUG, SERVICIOS

COCINAS = "/servicios/extraccion-cocinas-industriales/"
EXTRACCION = "/servicios/extraccion-de-aire/"
VENTILACION = "/servicios/ventilacion-inyeccion-de-aire/"
PRESURIZACION = "/servicios/presurizacion-de-escaleras/"
MANTENCION = "/servicios/mantencion-hvac/"


def _texto(html):
    return html_lib.unescape(html)


def _titulo(html):
    return _texto(html.split("<title>")[1].split("</title>")[0])


def _h1(html):
    return _texto(re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S).group(1))).strip()


def _descripcion(html):
    return _texto(html.split('name="description" content="')[1].split('"')[0])


def _texto_propio(servicio):
    """El texto que escribe ESTA pagina, sin la plantilla compartida."""
    partes = list(servicio["entrada"]) + list(servicio["incluye"])
    for seccion in servicio["secciones"]:
        partes += [seccion["h2"], *seccion["parrafos"], *seccion.get("lista", [])]
    for item in servicio["faq"]:
        partes += [item["p"], item["r"]]
    return partes


def _tejas(texto, k=5):
    palabras = re.findall(r"\w+", texto.lower())
    return {" ".join(palabras[i:i + k]) for i in range(len(palabras) - k + 1)}


class CocinasIndustrialesTests(TestCase):
    def test_title_h1_y_description_dicen_la_busqueda(self):
        html = self.client.get(COCINAS).content.decode()
        self.assertIn("Extracción de aire en cocinas industriales", _titulo(html))
        self.assertLessEqual(len(_titulo(html)), 60)
        self.assertIn("cocinas industriales", _h1(html))
        desc = _descripcion(html)
        self.assertLessEqual(len(desc), 155)
        for palabra in ("Campana", "inyección de aire", "cocinas industriales"):
            self.assertIn(palabra, desc)

    def test_responde_lo_que_busca_quien_tiene_una_cocina(self):
        """Autocompletado: campana con salida al exterior, inyección de aire en la
        cocina, por qué una campana industrial no funciona."""
        html = _texto(self.client.get(COCINAS).content.decode())
        for h2 in (
            "Campana, ducto y extractor: un solo recorrido hasta el exterior",
            "Inyección de aire: el aire que sale tiene que volver a entrar",
            "Por qué una campana industrial no saca el humo",
            "Qué conviene tener a mano para cotizar",
        ):
            self.assertIn(h2, html)
        self.assertIn("Filtros de la campana saturados de grasa", html)

    def test_no_repite_ningun_texto_de_la_pagina_de_extraccion(self):
        """Ni una frase de cocinas puede estar copiada en extracción, y su texto
        propio tiene que ser casi todo distinto."""
        cocinas, extraccion = POR_SLUG["extraccion-cocinas-industriales"], POR_SLUG["extraccion-de-aire"]
        html_extraccion = _texto(self.client.get(EXTRACCION).content.decode())
        for frase in _texto_propio(cocinas):
            if len(frase) > 40:
                with self.subTest(frase=frase[:60]):
                    self.assertNotIn(frase, html_extraccion)
        a = _tejas(" ".join(_texto_propio(cocinas)))
        b = _tejas(" ".join(_texto_propio(extraccion)))
        self.assertLess(len(a & b) / len(a), 0.1, "el texto de cocinas se repite en extracción")

    def test_no_usa_la_misma_foto_ni_el_mismo_titulo_de_proyectos(self):
        cocinas, extraccion = POR_SLUG["extraccion-cocinas-industriales"], POR_SLUG["extraccion-de-aire"]
        self.assertNotEqual(cocinas["imagen"], extraccion["imagen"])
        self.assertNotEqual(cocinas["titulo_proyectos"], extraccion["titulo_proyectos"])

    def test_extraccion_ya_no_compite_por_cocinas_y_la_enlaza(self):
        html = self.client.get(EXTRACCION).content.decode()
        self.assertNotIn("cocina", _h1(html).lower())
        self.assertNotIn("cocina", _titulo(html).lower())
        self.assertIn(f'class="servicio-seccion-enlace" href="{COCINAS}"', html)

    def test_la_portada_tiene_una_tarjeta_por_servicio(self):
        """La de cocinas no tenía tarjeta en la portada: solo el pie la enlazaba."""
        html = self.client.get("/").content.decode()
        grilla = html.split('id="servicios"')[1].split("</section>")[0]
        for servicio in SERVICIOS:
            with self.subTest(servicio=servicio["slug"]):
                self.assertIn(
                    f'service-card-link-wrap" href="/servicios/{servicio["slug"]}/"', grilla
                )
                self.assertIn(html_lib.escape(servicio["tarjeta"]), grilla)

    def test_el_sitemap_la_fecha_despues_de_publicarla(self):
        cuerpo = self.client.get("/sitemap.xml").content.decode()
        entrada = re.search(
            r"<loc>[^<]*" + re.escape(COCINAS) + r"</loc>\s*<lastmod>([0-9-]+)</lastmod>", cuerpo
        )
        self.assertIsNotNone(entrada)
        # Se publicó el 16-10-2026; un lastmod anterior le dice a Google que no hay nada nuevo.
        self.assertGreaterEqual(date.fromisoformat(entrada.group(1)), date(2026, 10, 16))


class InyeccionDeAireTests(TestCase):
    def test_title_y_h1_dicen_inyeccion_y_extraccion_de_aire(self):
        html = self.client.get(VENTILACION).content.decode()
        self.assertIn("inyección y extracción de aire", _titulo(html))
        self.assertLessEqual(len(_titulo(html)), 60)
        self.assertIn("inyección y extracción de aire", _h1(html))
        self.assertLessEqual(len(_descripcion(html)), 155)

    def test_explica_que_es_la_inyeccion_y_enlaza_a_cocinas(self):
        html = self.client.get(VENTILACION).content.decode()
        self.assertIn("Qué es la inyección de aire", _texto(html))
        self.assertIn("¿Qué es un sistema de inyección y extracción de aire?", _texto(html))
        self.assertIn(f'class="servicio-seccion-enlace" href="{COCINAS}"', html)


class PresurizacionTests(TestCase):
    def test_responde_sala_de_presurizacion_y_escalera_presurizada(self):
        html = _texto(self.client.get(PRESURIZACION).content.decode())
        self.assertIn("El equipo y la sala de presurización", html)
        self.assertIn("<summary>¿Qué es una escalera presurizada?</summary>", html)

    def test_enlaza_a_la_mantencion(self):
        html = self.client.get(PRESURIZACION).content.decode()
        self.assertIn(f'class="servicio-seccion-enlace" href="{MANTENCION}"', html)


class MantencionParaEmpresasTests(TestCase):
    def test_apunta_a_la_busqueda_de_empresas(self):
        html = self.client.get(MANTENCION).content.decode()
        titulo = _titulo(html)
        self.assertIn("aire acondicionado", titulo)
        self.assertIn("empresas", titulo)
        self.assertLessEqual(len(titulo), 60)
        self.assertIn("empresas", _h1(html))
        desc = _descripcion(html)
        self.assertLessEqual(len(desc), 155)
        for palabra in ("extractores", "presurización", "empresas"):
            self.assertIn(palabra, desc)

    def test_cubre_extractores_y_presurizacion_y_enlaza(self):
        html = self.client.get(MANTENCION).content.decode()
        self.assertIn("Mantención de extractores, ventilación y presurización", _texto(html))
        self.assertIn(f'class="servicio-seccion-enlace" href="{PRESURIZACION}"', html)


class SinH2RepetidosEntreServiciosTests(TestCase):
    def test_ningun_h2_propio_se_repite_en_otro_servicio(self):
        """Dos páginas con el mismo subtítulo responden la misma pregunta."""
        vistos = {}
        for servicio in SERVICIOS:
            for seccion in servicio["secciones"]:
                vistos.setdefault(seccion["h2"], []).append(servicio["slug"])
        repetidos = {h2: s for h2, s in vistos.items() if len(s) > 1}
        self.assertEqual(repetidos, {})


class IndiceDeServiciosTests(TestCase):
    def test_el_conteo_de_lineas_de_trabajo_es_el_real(self):
        html = self.client.get("/servicios/").content.decode()
        self.assertIn(f"{len(SERVICIOS)} líneas de trabajo", html)
        self.assertNotIn("Seis líneas de trabajo", html)


class EntidadUnicaTests(TestCase):
    def test_la_empresa_y_el_sitio_declaran_la_misma_url(self):
        import json

        html = self.client.get("/").content.decode()
        bloques = []
        for crudo in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            dato = json.loads(crudo)
            bloques.extend(dato.get("@graph", [dato]))
        empresa = [b for b in bloques if b.get("@type") == "HVACBusiness"][0]
        sitio = [b for b in bloques if b.get("@type") == "WebSite"][0]
        canonical = html.split('rel="canonical" href="')[1].split('"')[0]
        self.assertEqual(empresa["url"], sitio["url"])
        self.assertEqual(empresa["url"], canonical)
