"""Semana SEO del 16-11-2026: ventilación y presurización le hablan a quien contrata.

Search Console por la API (igual a lo que informó Windsor), 08 al 14-11: 5 clics,
274 impresiones, posición 7,52. Ventilación: 27 impresiones, posición 12, 0
clics. Presurización: 21 impresiones, posición 9,3, 0 clics. El title y el H1 de
las dos se dejan como están: los de ventilación cambiaron el 03-11 y se miden el
17-11 y el 01-12.

Lo que se cambia, y estas pruebas cuidan:
- La description de las dos le habla a la constructora, la inmobiliaria o el
  edificio, y pide la cotización.
- Las obras que el texto nombra enlazan a su ficha (antes solo la grilla del
  final llegaba a ellas).
- Enlaces dentro del texto entre ventilación, extracción y presurización.
- Un bloque "Para cotizar..." con lo que sirve enviar y un botón al formulario.
- La fila "Especialidades" de cada ficha de proyecto enlaza a su servicio.

Regla de la semana: solo se reescriben hechos que el sitio ya publica. Nada de
normas, certificaciones, sectores ni clientes nuevos: eso lo confirma la empresa.
"""
import html as html_lib
import re
from datetime import date

from django.test import TestCase

from core.servicios import POR_SLUG, SERVICIOS
from portfolio.catalog import get_project_catalog

VENTILACION = "/servicios/ventilacion-inyeccion-de-aire/"
PRESURIZACION = "/servicios/presurizacion-de-escaleras/"
EXTRACCION = "/servicios/extraccion-de-aire/"
COCINAS = "/servicios/extraccion-cocinas-industriales/"
PROYECTOS = {p["slug"]: p for p in get_project_catalog()["projects"]}

CTA_VENTILACION = "Para cotizar la ventilación de una obra o un edificio"
CTA_PRESURIZACION = "Para cotizar la presurización de una obra o un edificio"


def _texto(html):
    return html_lib.unescape(html)


def _titulo(html):
    return _texto(html.split("<title>")[1].split("</title>")[0])


def _h1(html):
    return _texto(re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S).group(1))).strip()


def _descripcion(html):
    return _texto(html.split('name="description" content="')[1].split('"')[0])


def _seccion(html, h2):
    """El HTML de la sección de texto cuyo H2 es `h2` (falla si no existe).

    Corta en el primer </div>: la sección no anida divs. Sin ese corte, la última
    sección se llevaba el resto de la página, con la grilla de proyectos incluida,
    y la prueba de "obras enlazadas" pasaba contra el código viejo (comprobado al
    revés el 16-11).
    """
    for bloque in html.split('<div class="servicio-seccion">')[1:]:
        if h2 in _texto(bloque.split("</h2>")[0]):
            return bloque.split("</div>")[0]
    raise AssertionError(f"no está la sección {h2!r}")


def _h2s(html):
    return [_texto(re.sub(r"<[^>]+>", "", h)).strip() for h in re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.S)]


class VentilacionParaQuienContrataTests(TestCase):
    def setUp(self):
        self.html = self.client.get(VENTILACION).content.decode()

    def test_description_habla_a_quien_contrata_y_pide_la_cotizacion(self):
        desc = _descripcion(self.html)
        self.assertLessEqual(len(desc), 155)
        for palabra in ("Proyectos de ventilación", "constructoras", "retail", "salud", "cotización"):
            self.assertIn(palabra, desc)

    def test_title_y_h1_del_03_11_quedan_quietos_para_medirlos(self):
        self.assertEqual(_titulo(self.html), "Ventilación, inyección y extracción de aire | Max Services")
        self.assertEqual(_h1(self.html), "Ventilación, inyección y extracción de aire en Santiago")

    def test_bloque_para_cotizar_con_boton_al_formulario(self):
        bloque = _seccion(self.html, CTA_VENTILACION)
        self.assertIn('class="btn btn-brand-primary servicio-seccion-cta" href="#formulario"', bloque)
        self.assertIn("Cotizar la ventilación del proyecto", bloque)
        self.assertIn("Si es una obra nueva o un edificio que ya está en uso", _texto(bloque))
        self.assertIn('id="formulario"', self.html)

    def test_las_obras_nombradas_enlazan_a_su_ficha(self):
        bloque = _seccion(self.html, "Ventilación en obra nueva y en edificios en uso")
        for slug in ("obra-echeverria-izquierdo-edificaciones", "obra-tasco-boetsch-en-ejecucion",
                     "edificio-patrimonial-ladrillo"):
            with self.subTest(slug=slug):
                self.assertIn(f'href="/proyectos/{slug}/"', bloque)

    def test_enlaza_dentro_del_texto_a_extraccion_y_a_presurizacion(self):
        self.assertIn(f'class="servicio-seccion-enlace" href="{EXTRACCION}"', self.html)
        self.assertIn(f'class="servicio-seccion-enlace" href="{PRESURIZACION}"', self.html)


class PresurizacionParaQuienContrataTests(TestCase):
    def setUp(self):
        self.html = self.client.get(PRESURIZACION).content.decode()

    def test_description_habla_a_quien_contrata_y_pide_la_cotizacion(self):
        desc = _descripcion(self.html)
        self.assertLessEqual(len(desc), 155)
        for palabra in ("Presurización de escaleras", "constructoras", "inmobiliarias", "mantención",
                        "cotización"):
            self.assertIn(palabra, desc)

    def test_title_y_h1_no_cambian(self):
        self.assertEqual(_titulo(self.html), "Presurización de escaleras en Santiago | Max Services")
        self.assertEqual(_h1(self.html), "Presurización de caja de escaleras para edificios en Santiago")

    def test_bloque_para_cotizar_con_boton_al_formulario(self):
        bloque = _seccion(self.html, CTA_PRESURIZACION)
        self.assertIn('class="btn btn-brand-primary servicio-seccion-cta" href="#formulario"', bloque)
        self.assertIn("Cotizar la presurización del edificio", bloque)
        self.assertIn("Los planos de arquitectura del edificio", _texto(bloque))

    def test_las_obras_con_presurizacion_enlazan_a_su_ficha(self):
        bloque = _seccion(self.html, "Presurización en obra, coordinada con la constructora")
        for slug in ("edificio-residencial-vista-parque", "edificio-residencial-tasco-boetsch",
                     "obra-inmobiliaria-la-fontana-11-pisos", "obra-echeverria-izquierdo-edificaciones",
                     "obra-tasco-boetsch-en-ejecucion"):
            with self.subTest(slug=slug):
                self.assertIn(f'href="/proyectos/{slug}/"', bloque)

    def test_enlaza_a_la_inyeccion_de_aire(self):
        self.assertIn(f'class="servicio-seccion-enlace" href="{VENTILACION}"', self.html)

    def test_no_publica_normas_ni_certificaciones_sin_confirmar(self):
        """Guarda: ninguna norma ni certificación está confirmada por la empresa."""
        texto = _texto(re.sub(r"<[^>]+>", " ", self.html))
        # Las siglas van con mayúsculas y palabra completa: "nch" sin más calza "Lynch".
        self.assertIsNone(re.search(r"\b(NFPA|OGUC|NCh)\b", texto))
        self.assertIsNone(re.search(r"ordenanza|certific|decreto", texto, re.I))


class EnlacesHaciaLasDosPaginasTests(TestCase):
    def test_extraccion_enlaza_a_ventilacion_dentro_del_texto(self):
        html = self.client.get(EXTRACCION).content.decode()
        self.assertIn(f'class="servicio-seccion-enlace" href="{VENTILACION}"', html)

    def test_la_ficha_enlaza_cada_especialidad_a_su_servicio(self):
        html = self.client.get("/proyectos/edificio-residencial-vista-parque/").content.decode()
        fila = html.split("<span>Especialidades</span>")[1].split("</div>")[0]
        self.assertIn(f'<a href="{PRESURIZACION}">Presurización</a>', fila)
        self.assertIn(f'<a href="{VENTILACION}">Ventilación</a>', fila)
        self.assertIn('<a href="/servicios/climatizacion-aire-acondicionado/">Climatización</a>', fila)

    def test_todas_las_fichas_enlazan_sus_especialidades_y_proyectos_queda_sin_enlace(self):
        from core.servicios import especialidades_del_proyecto

        for slug, proyecto in PROYECTOS.items():
            html = self.client.get(f"/proyectos/{slug}/").content.decode()
            fila = html.split("<span>Especialidades</span>")[1].split("</div>")[0]
            for e in especialidades_del_proyecto(proyecto):
                with self.subTest(proyecto=slug, especialidad=e["nombre"]):
                    if e["slug"]:
                        self.assertIn(f'<a href="/servicios/{e["slug"]}/">{e["nombre"]}</a>', fila)
                    else:
                        self.assertNotIn(f'>{e["nombre"]}</a>', fila)
        # Extracción va a extracción de aire (no a cocinas) y Mantención a mantención.
        mapa = {e["nombre"]: e["slug"] for p in PROYECTOS.values() for e in especialidades_del_proyecto(p)}
        self.assertEqual(mapa["Extracción"], "extraccion-de-aire")
        self.assertEqual(mapa["Mantención"], "mantencion-hvac")
        self.assertIsNone(mapa["Proyectos"])

    def test_cada_obra_enlazada_existe_y_tiene_la_especialidad_del_servicio(self):
        """No se enlaza una obra que no hizo ese servicio: sería afirmar algo falso."""
        for servicio in SERVICIOS:
            etiquetas = set(servicio.get("etiquetas_proyectos", []))
            for seccion in servicio["secciones"]:
                for slug in seccion.get("obras", []):
                    with self.subTest(servicio=servicio["slug"], obra=slug):
                        self.assertIn(slug, PROYECTOS)
                        self.assertTrue(etiquetas & set(PROYECTOS[slug]["services"]))


class SinEnlacesRotosNiH2RepetidosTests(TestCase):
    """Guardas que pidió el director SEO: enlaces rotos, H2 duplicados, canonical."""

    def test_todo_enlace_interno_de_las_dos_paginas_responde_200(self):
        for ruta in (VENTILACION, PRESURIZACION):
            html = self.client.get(ruta).content.decode()
            destinos = {h.split("#")[0] for h in re.findall(r'href="(/[^"]*)"', html)}
            destinos = {d for d in destinos if d and not d.startswith("/static/")}
            self.assertTrue(destinos)
            for destino in sorted(destinos):
                with self.subTest(pagina=ruta, destino=destino):
                    self.assertEqual(self.client.get(destino).status_code, 200)

    def test_ningun_h2_se_repite_dentro_de_la_pagina(self):
        for ruta in (VENTILACION, PRESURIZACION):
            h2s = _h2s(self.client.get(ruta).content.decode())
            with self.subTest(ruta=ruta):
                self.assertEqual(len(h2s), len(set(h2s)), h2s)

    def test_canonical_apunta_a_la_misma_pagina(self):
        for ruta in (VENTILACION, PRESURIZACION):
            html = self.client.get(ruta).content.decode()
            canonical = html.split('rel="canonical" href="')[1].split('"')[0]
            with self.subTest(ruta=ruta):
                self.assertTrue(canonical.endswith(ruta), canonical)

    def test_los_bloques_para_cotizar_no_se_copian_entre_paginas(self):
        """Cada bloque tiene que ser propio: casi copias son lo que Google no indexa."""
        bloques = {
            VENTILACION: [s for s in POR_SLUG["ventilacion-inyeccion-de-aire"]["secciones"]
                          if s["h2"] == CTA_VENTILACION][0],
            PRESURIZACION: [s for s in POR_SLUG["presurizacion-de-escaleras"]["secciones"]
                            if s["h2"] == CTA_PRESURIZACION][0],
        }
        for ruta, seccion in bloques.items():
            frases = [f for f in seccion["parrafos"] + seccion["lista"] if len(f) > 30]
            for otra in (VENTILACION, PRESURIZACION, COCINAS, EXTRACCION):
                if otra == ruta:
                    continue
                html = _texto(self.client.get(otra).content.decode())
                for frase in frases:
                    with self.subTest(de=ruta, en=otra, frase=frase[:50]):
                        self.assertNotIn(frase, html)


class SitemapTests(TestCase):
    def test_las_dos_paginas_anuncian_la_revision_del_16_11(self):
        cuerpo = self.client.get("/sitemap.xml").content.decode()
        for ruta in (VENTILACION, PRESURIZACION):
            entrada = re.search(r"<loc>[^<]*" + re.escape(ruta) + r"</loc>\s*<lastmod>([0-9-]+)</lastmod>",
                                cuerpo)
            with self.subTest(ruta=ruta):
                self.assertEqual(date.fromisoformat(entrada.group(1)), date(2026, 11, 16))
