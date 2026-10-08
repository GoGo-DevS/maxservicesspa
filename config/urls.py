"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from core.views import recurso_retirado, robots_txt, sitemap_xml

urlpatterns = [
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap_xml, name='sitemap_xml'),
    # Restos del sitio anterior que Google seguia rastreando: 410, no 404.
    path('index.rdf', recurso_retirado, name='retirado_index_rdf'),
    path('rss.xml', recurso_retirado, name='retirado_rss_xml'),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('proyectos/', include('portfolio.urls')),
]
