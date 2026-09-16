from django.test import TestCase
from django.urls import reverse

from portfolio.catalog import get_project_catalog


class ProjectsViewTests(TestCase):
    def test_projects_page_responds_successfully(self):
        response = self.client.get(reverse("portfolio:projects_index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/projects.html")

# Create your tests here.


class FichasDeProyectoTests(TestCase):
    """Cada proyecto con URL propia (16-09-2026).

    Las 16 fichas se dibujaban con JavaScript dentro de /proyectos/: para Google
    eran UNA sola pagina y todo ese texto no servia para aparecer en busquedas.
    """

    def test_todas_las_fichas_responden_y_muestran_su_contenido(self):
        for proyecto in get_project_catalog()["projects"]:
            with self.subTest(proyecto=proyecto["slug"]):
                r = self.client.get(f"/proyectos/{proyecto['slug']}/")
                self.assertEqual(r.status_code, 200)
                self.assertContains(r, proyecto["name"])
                self.assertContains(r, proyecto["location"])

    def test_un_proyecto_inventado_da_404(self):
        self.assertEqual(self.client.get("/proyectos/no-existe/").status_code, 404)

    def test_el_indice_enlaza_cada_ficha_en_el_html(self):
        """Los enlaces tienen que estar en el HTML, no dibujarse con JavaScript."""
        html = self.client.get("/proyectos/").content.decode()
        for proyecto in get_project_catalog()["projects"]:
            self.assertIn(f"/proyectos/{proyecto['slug']}/", html)

    def test_cada_ficha_trae_su_title_propio(self):
        titulos = set()
        for proyecto in get_project_catalog()["projects"][:5]:
            html = self.client.get(f"/proyectos/{proyecto['slug']}/").content.decode()
            titulo = html.split("<title>")[1].split("</title>")[0]
            self.assertLessEqual(len(titulo), 75)
            titulos.add(titulo)
        self.assertEqual(len(titulos), 5, "hay fichas con el mismo title")
