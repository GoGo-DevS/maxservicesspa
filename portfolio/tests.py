from django.test import TestCase
from django.urls import reverse


class ProjectsViewTests(TestCase):
    def test_projects_page_responds_successfully(self):
        response = self.client.get(reverse("portfolio:projects_index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/projects.html")

# Create your tests here.
