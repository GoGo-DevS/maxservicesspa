"""SEO on-page del 07-10-2026.

Search Console a 28 dias: 9 clics, 439 impresiones, posicion 10,3. Los seis
servicios en la pagina 2, 15 de 16 fichas de proyecto "descubierta, sin
indexar", y /index.rdf y /rss.xml del sitio anterior todavia rastreados. Estas
pruebas cuidan lo que se arreglo para que un cambio futuro no lo deshaga sin
que nadie se entere.
"""
import html as html_lib
import json
import re
from pathlib import Path

from django.conf import settings
from django.test import TestCase, override_settings

from core.servicios import SERVICIOS, proyectos_del_servicio
from portfolio.catalog import get_project_catalog

PROYECTOS = get_project_catalog()["projects"]

RUTAS = (
    ["/", "/servicios/", "/proyectos/", "/empresa/", "/contacto/"]
    + [f"/servicios/{s['slug']}/" for s in SERVICIOS]
    + [f"/proyectos/{p['slug']}/" for p in PROYECTOS]
)

LD_JSON = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

# Formas del voseo que no pueden aparecer en un sitio chileno que trata de tu.
VOSEO = re.compile(
    # Solo las formas con tilde: "contacta" o "llama" sin tilde son del tu.
    r"\b(querés|tenés|podés|sabés|necesitás|contactá|llamá|mirá|solicitá|cotizá|escribinos)\b",
    re.I,
)


def _bloques(html):
    """Todos los JSON-LD de la pagina, ya parseados con json.loads."""
    salida = []
    for crudo in LD_JSON.findall(html):
        dato = json.loads(crudo)
        salida.extend(dato["@graph"] if "@graph" in dato else [dato])
    return salida


def _titulo(html):
    return html_lib.unescape(html.split("<title>")[1].split("</title>")[0])


def _descripcion(html):
    return html_lib.unescape(html.split('name="description" content="')[1].split('"')[0])


class SeoOnPageTests(TestCase):
    def setUp(self):
        self.paginas = {}

    def _get(self, ruta):
        if ruta not in self.paginas:
            r = self.client.get(ruta)
            self.assertEqual(r.status_code, 200, ruta)
            self.paginas[ruta] = r.content.decode()
        return self.paginas[ruta]

    def test_todo_el_json_ld_parsea(self):
        """Un JSON-LD mal formado se ve igual en pantalla y Google lo descarta entero."""
        for ruta in RUTAS:
            with self.subTest(ruta=ruta):
                bloques = _bloques(self._get(ruta))
                self.assertTrue(bloques, f"{ruta} sin datos estructurados")

    def test_titles_y_descriptions_caben_y_no_se_repiten(self):
        titulos, descripciones = {}, {}
        for ruta in RUTAS:
            html = self._get(ruta)
            titulo, desc = _titulo(html), _descripcion(html)
            with self.subTest(ruta=ruta):
                self.assertLessEqual(len(titulo), 60, f"title de {len(titulo)}: {titulo}")
                self.assertLessEqual(len(desc), 155, f"description de {len(desc)}: {desc}")
                self.assertTrue(desc.strip())
            titulos.setdefault(titulo, []).append(ruta)
            descripciones.setdefault(desc, []).append(ruta)
        self.assertEqual([r for r in titulos.values() if len(r) > 1], [], "titles repetidos")
        self.assertEqual([r for r in descripciones.values() if len(r) > 1], [], "descriptions repetidas")

    def test_la_home_nombra_la_marca_y_lo_que_hace(self):
        html = self._get("/")
        titulo = _titulo(html)
        self.assertTrue(titulo.startswith("Max Services SpA"), titulo)
        self.assertIn("Climatización", titulo)
        sitio = [b for b in _bloques(html) if b.get("@type") == "WebSite"]
        self.assertEqual(len(sitio), 1)
        self.assertEqual(sitio[0]["name"], "Max Services SpA")

    def test_la_empresa_es_una_sola_entidad(self):
        """El Service de cada pagina apunta a la misma empresa que declara el sitio."""
        empresa = [b for b in _bloques(self._get("/")) if b.get("@type") == "HVACBusiness"][0]
        self.assertEqual(empresa["legalName"], "MAX SERVICES SpA")
        self.assertIn("Max Services", empresa["alternateName"])
        self.assertEqual(empresa["telephone"], "+56225590108")
        for servicio in SERVICIOS:
            bloques = _bloques(self._get(f"/servicios/{servicio['slug']}/"))
            service = [b for b in bloques if b.get("@type") == "Service"][0]
            self.assertEqual(service["provider"]["@id"], empresa["@id"])

    def test_cada_servicio_trae_h1_h2_faq_y_migas(self):
        for servicio in SERVICIOS:
            ruta = f"/servicios/{servicio['slug']}/"
            html = self._get(ruta)
            with self.subTest(ruta=ruta):
                self.assertEqual(html.count("<h1"), 1)
                for seccion in servicio["secciones"]:
                    self.assertIn(html_lib.escape(seccion["h2"]), html)
                tipos = {b.get("@type") for b in _bloques(html)}
                self.assertTrue({"Service", "BreadcrumbList", "FAQPage"} <= tipos, tipos)

    def test_el_faq_del_schema_esta_visible_en_la_pagina(self):
        """FAQPage con preguntas que no se ven es exactamente lo que Google penaliza."""
        for servicio in SERVICIOS:
            html = self._get(f"/servicios/{servicio['slug']}/")
            visible = html_lib.unescape(html)
            faq = [b for b in _bloques(html) if b.get("@type") == "FAQPage"][0]
            self.assertEqual(len(faq["mainEntity"]), len(servicio["faq"]))
            for pregunta in faq["mainEntity"]:
                with self.subTest(pregunta=pregunta["name"]):
                    self.assertIn(f"<summary>{pregunta['name']}</summary>", visible)
                    self.assertIn(pregunta["acceptedAnswer"]["text"], visible)

    def test_cada_servicio_enlaza_sus_proyectos(self):
        for servicio in SERVICIOS:
            html = self._get(f"/servicios/{servicio['slug']}/")
            esperados = proyectos_del_servicio(servicio, PROYECTOS)
            self.assertTrue(esperados, servicio["slug"])
            for proyecto in esperados:
                self.assertIn(f'href="/proyectos/{proyecto["slug"]}/"', html)

    def test_ninguna_ficha_de_proyecto_queda_sin_enlace_desde_un_servicio(self):
        """La causa de "descubierta, sin indexar": solo /proyectos/ las enlazaba."""
        enlazadas = set()
        for servicio in SERVICIOS:
            html = self._get(f"/servicios/{servicio['slug']}/")
            enlazadas |= set(re.findall(r'href="/proyectos/([a-z0-9-]+)/"', html))
        faltan = {p["slug"] for p in PROYECTOS} - enlazadas
        self.assertEqual(faltan, set())

    def test_la_ficha_enlaza_sus_servicios_y_proyectos_parecidos(self):
        for proyecto in PROYECTOS:
            html = self._get(f"/proyectos/{proyecto['slug']}/")
            with self.subTest(proyecto=proyecto["slug"]):
                self.assertIn('href="/servicios/', html)
                otros = set(re.findall(r'href="/proyectos/([a-z0-9-]+)/"', html)) - {proyecto["slug"]}
                self.assertEqual(len(otros), 3)

    def test_las_fichas_relacionadas_no_son_siempre_las_mismas(self):
        """Antes las 16 fichas enlazaban a los mismos tres primeros proyectos."""
        juegos = set()
        for proyecto in PROYECTOS:
            html = self._get(f"/proyectos/{proyecto['slug']}/")
            otros = frozenset(re.findall(r'href="/proyectos/([a-z0-9-]+)/"', html)) - {proyecto["slug"]}
            juegos.add(otros)
        self.assertGreater(len(juegos), 4)

    def test_sin_voseo_ni_plantilla_impresa(self):
        for ruta in RUTAS:
            html = self._get(ruta)
            texto = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
            with self.subTest(ruta=ruta):
                self.assertIsNone(VOSEO.search(html_lib.unescape(texto)))
                self.assertNotIn("{#", html)
                self.assertNotIn("{%", html)

    def test_la_home_lleva_a_la_ficha_de_cada_proyecto_destacado(self):
        js = (Path(settings.BASE_DIR) / "static/js/home-projects.js").read_text(encoding="utf-8")
        self.assertIn('link.href = projectsUrl + project.slug + "/";', js)


class RestosDelSitioAnteriorTests(TestCase):
    def test_index_rdf_y_rss_dan_410(self):
        for ruta in ["/index.rdf", "/rss.xml"]:
            with self.subTest(ruta=ruta):
                self.assertEqual(self.client.get(ruta).status_code, 410)

    def test_una_ruta_inventada_sigue_dando_404(self):
        """El 410 es solo para esas dos: lo demas que no existe sigue siendo 404."""
        self.assertEqual(self.client.get("/feed-que-nunca-existio.xml").status_code, 404)

    def test_el_sitemap_sigue_bien_y_trae_lastmod(self):
        r = self.client.get("/sitemap.xml")
        self.assertEqual(r.status_code, 200)
        cuerpo = r.content.decode()
        total = 5 + len(SERVICIOS) + len(PROYECTOS)
        self.assertEqual(cuerpo.count("<loc>"), total)
        self.assertEqual(total, 27)
        self.assertEqual(cuerpo.count("<lastmod>"), total)
        self.assertNotIn("index.rdf", cuerpo)
        self.assertNotIn("rss.xml", cuerpo)


@override_settings(GA4_MEASUREMENT_ID="G-PRUEBA1234")
class MedicionIntactaTests(TestCase):
    def test_los_eventos_de_contacto_siguen_cargando(self):
        html = self.client.get("/servicios/mantencion-hvac/").content.decode()
        self.assertIn("js/medicion-contactos", html)
        js = (Path(settings.BASE_DIR) / "static/js/medicion-contactos.js").read_text(encoding="utf-8")
        for evento in ["contacto_whatsapp", "contacto_telefono", "contacto_email", "formulario_enviado"]:
            self.assertIn(evento, js)
