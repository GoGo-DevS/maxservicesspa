import logging
from smtplib import SMTPException
from urllib.parse import urlparse
from xml.sax.saxutils import escape

from django.conf import settings
from django.contrib import messages
from django.core.mail import BadHeaderError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from core.emailing import send_contact_request_notification
from core.forms import ContactRequestForm
from core.locations import get_city_choices, get_commune_choices
from core.seo import absolute_static_url
from core.sitemaps import StaticViewSitemap
from portfolio.catalog import get_project_catalog


logger = logging.getLogger(__name__)


class SitemapSite:
    def __init__(self, domain):
        self.domain = domain


def home(request):
    if request.method == "POST":
        contact_form = ContactRequestForm(request.POST)
        if contact_form.is_valid():
            contact_request = contact_form.save()
            try:
                send_contact_request_notification(contact_request)
                messages.success(
                    request,
                    "Solicitud enviada correctamente. El equipo revisará los antecedentes y responderá a la brevedad.",
                )
            except (OSError, SMTPException, BadHeaderError) as exc:
                logger.exception(
                    "Contact form email notification failed. exception_type=%s exception_message=%s password_present=%s",
                    exc.__class__.__name__,
                    str(exc),
                    bool(settings.EMAIL_HOST_PASSWORD),
                )
                messages.warning(
                    request,
                    "La solicitud fue registrada correctamente, pero el aviso por correo no pudo enviarse en este momento.",
                )
            return redirect(f"{reverse('core:home')}?focus=formulario")
    else:
        contact_form = ContactRequestForm()

    return render(
        request,
        "core/home.html",
        {
            "page_title": "MAX SERVICES SPA | Climatización, ventilación y proyectos HVAC",
            "page_description": "Empresa de climatización y ventilación en Santiago. Instalación, mantención, extracción, presurización, inyección de aire y proyectos HVAC para empresas, edificios e instituciones.",
            "canonical_path": "/",
            "og_image": absolute_static_url("assets/home/hero-main.png"),
            "project_catalog": get_project_catalog(),
            "contact_form": contact_form,
            "experience_highlights": [
                {
                    "label": "Inicio de operaciones",
                    "value": "Desde 2011",
                    "description": "Trayectoria continua en climatización, mantención y ejecución técnica.",
                },
                {
                    "label": "Experiencia aplicada",
                    "value": "Retail, salud, universidades, oficinas y edificios",
                    "description": "Proyectos ejecutados en Santiago y regiones para distintos tipos de cliente.",
                },
                {
                    "label": "Tipo de servicio",
                    "value": "Diseño, suministro, montaje y mantención",
                    "description": "Soluciones HVAC para comercio, instituciones, edificios y obras.",
                },
            ],
            "featured_clients": [
                {
                    "name": "Boetsch",
                    "logo": "assets/clients/grid/logo-boetsch.svg",
                    "logo_alt": "Logo de Boetsch",
                    "logo_class": "logo-standard-wide",
                    "url": "https://boetsch.cl/",
                },
                {
                    "name": "Echeverría Izquierdo",
                    "logo": "assets/clients/grid/echeverria_izq.png",
                    "logo_alt": "Logo de Echeverría Izquierdo",
                    "logo_class": "logo-scale-up",
                    "url": "https://eiii.cl/",
                },
                {
                    "name": "Gespania",
                    "logo": "assets/clients/grid/gespania.svg",
                    "logo_alt": "Logo de Gespania",
                    "logo_class": "logo-standard-wide",
                },
                {
                    "name": "Carrán",
                    "logo": "assets/clients/grid/carran.png",
                    "logo_alt": "Logo de Carrán",
                    "logo_class": "logo-scale-up-sm",
                },
                {
                    "name": "Siena",
                    "logo": "assets/clients/grid/siena.svg",
                    "logo_alt": "Logo de Siena",
                    "logo_class": "logo-scale-up",
                    "url": "https://www.siena.cl/",
                },
                {
                    "name": "Universidad Diego Portales",
                    "logo": "assets/clients/grid/Logo_Universidad_Diego_Portales.png",
                    "logo_alt": "Logo de Universidad Diego Portales",
                    "logo_class": "logo-scale-up-sm",
                    "url": "https://www.udp.cl/",
                },
                {
                    "name": "Hospital Luis Calvo Mackenna",
                    "logo": "assets/clients/grid/hospital_lcm.png",
                    "logo_alt": "Logo de Hospital Luis Calvo Mackenna",
                    "logo_class": "logo-scale-up-lg",
                    "url": "https://www.calvomackenna.cl/",
                },
                {
                    "name": "Universidad Autónoma de Chile",
                    "logo": "assets/clients/grid/Universidad-autonoma-de-chile.png",
                    "logo_alt": "Logo de Universidad Autónoma de Chile",
                    "logo_class": "logo-scale-up-sm",
                    "url": "https://www.uautonoma.cl/",
                },
                {
                    "name": "SYP",
                    "logo": "assets/clients/grid/syp.svg",
                    "logo_alt": "Logo de SYP",
                    "logo_class": "logo-scale-up-lg",
                    "url": "https://syplimitada.cl/",
                },
                {
                    "name": "Desco",
                    "logo": "assets/clients/grid/logo_desco_transparente-1536x428.png",
                    "logo_alt": "Logo de Desco",
                    "logo_class": "logo-scale-up",
                },
                {
                    "name": "Ormuz",
                    "logo": "assets/clients/grid/ormuz.png",
                    "logo_alt": "Logo de Ormuz",
                    "logo_class": "logo-scale-up-max",
                },
                {
                    "name": "Moller y Pérez-Cotapos",
                    "logo": "assets/clients/grid/Moller y Pérez-Cotapos.png",
                    "logo_alt": "Logo de Moller y Pérez-Cotapos",
                    "logo_class": "logo-scale-up",
                    "url": "https://www.mpc.cl/",
                },
            ],
            "additional_clients": [
                {
                    "name": "Ingevec",
                    "logo": "assets/clients/grid/Ingevec.png",
                    "logo_alt": "Logo de Ingevec",
                    "url": "https://www.ingevec.cl/",
                },
                {
                    "name": "Tasco",
                    "logo": "assets/clients/marquee/logotasco.png",
                    "logo_alt": "Logo de Tasco",
                },
                {
                    "name": "Cerro Apoquindo",
                    "logo": "assets/clients/marquee/apoq4.png",
                    "logo_alt": "Logo de Cerro Apoquindo",
                },
                {
                    "name": "Befco",
                    "logo": "assets/clients/marquee/logo-befco-amarillo.png",
                    "logo_alt": "Logo de Befco",
                },
                {
                    "name": "Patriarca",
                    "logo": "assets/clients/marquee/logopatriarca.png",
                    "logo_alt": "Logo de Patriarca",
                },
                {
                    "name": "Francisco Lorca",
                    "logo": "assets/clients/marquee/Francisco Lorca.svg",
                    "logo_alt": "Logo de Francisco Lorca",
                },
                {
                    "name": "Pacal",
                    "logo": "assets/clients/marquee/pacal.png",
                    "logo_alt": "Logo de Pacal",
                    "url": "https://www.pacal.cl/",
                },
                {
                    "name": "Grevia",
                    "logo": "assets/clients/marquee/grevia_logo.png",
                    "logo_alt": "Logo de Grevia",
                },
                {
                    "name": "Magal",
                    "logo": "assets/clients/marquee/imagotipo-magal.svg",
                    "logo_alt": "Logo de Magal",
                },
                {
                    "name": "Brimac",
                    "logo": "assets/clients/marquee/brimac.svg",
                    "logo_alt": "Logo de Brimac",
                },
                {"name": "ICAAD"},
                {"name": "Paseo Las Condes"},
                {
                    "name": "San Fernando",
                    "logo": "assets/clients/marquee/c_sanfernando.png",
                    "logo_alt": "Logo de San Fernando",
                },
                {
                    "name": "El Volcán",
                    "logo": "assets/clients/marquee/logo_elvolcan.png",
                    "logo_alt": "Logo de El Volcán",
                    "url": "https://www.elvolcan.cl/",
                },
                {
                    "name": "DVC",
                    "logo": "assets/clients/marquee/logo-DVC.png",
                    "logo_alt": "Logo de DVC",
                },
                {"name": "René Corvalán"},
                {"name": "TROI Calvo Mackenna"},
                {"name": "Comunidades residenciales"},
            ],
            "project_sectors": [
                {
                    "title": "Retail y supermercados",
                    "description": "Remodelaciones y habilitaciones técnicas para recintos de alto flujo.",
                    "examples": "Hiper Líder Departamental y Líder General Velásquez.",
                },
                {
                    "title": "Salud y recintos clínicos",
                    "description": "Trabajos donde continuidad y control del aire son clave.",
                    "examples": "Hospital Luis Calvo Mackenna y TROI Calvo Mackenna.",
                },
                {
                    "title": "Universidades e instituciones",
                    "description": "Climatización y aire para recintos educacionales e institucionales.",
                    "examples": "Universidad Diego Portales y Universidad Autónoma de Chile.",
                },
                {
                    "title": "Oficinas y corporativo",
                    "description": "Climatización y confort para espacios de trabajo.",
                    "examples": "Oficinas Inverko y proyectos corporativos.",
                },
                {
                    "title": "Edificios y comunidades",
                    "description": "Montaje, presurización y mantención para operación continua.",
                    "examples": "Comunidades, edificios y proyectos inmobiliarios.",
                },
                {
                    "title": "Constructoras e inmobiliarias",
                    "description": "Apoyo técnico en obra, montaje y proyectos HVAC.",
                    "examples": "Boetsch, Echeverría Izquierdo, Carrán, Gespania, Desco y Ormuz.",
                },
            ],
            "brand_partners": [
                {
                    "name": "CLARK",
                    "logo": "assets/brands/clark.webp",
                    "logo_class": "brand-logo-clark",
                    "url": "https://clark-airconditioning.com/",
                },
                {
                    "name": "LG",
                    "logo": "assets/brands/lg.png",
                    "logo_class": "brand-logo-lg",
                    "url": "https://www.lg.com/cl/aire-acondicionado/",
                },
                {
                    "name": "BRAVO AIRES",
                    "logo": "assets/brands/bravo-aires.png",
                    "logo_class": "brand-logo-bravo",
                    "url": "https://bravoclimatizacion.cl/",
                },
                {
                    "name": "FRIGAIR",
                    "logo": "assets/brands/frigair.png",
                    "logo_class": "brand-logo-frigair",
                },
                {
                    "name": "GREE",
                    "logo": "assets/brands/gree.png",
                    "logo_class": "brand-logo-gree",
                    "url": "https://www.gree.cl/",
                },
                {
                    "name": "ANWO",
                    "logo": "assets/brands/anwo.png",
                    "logo_class": "brand-logo-anwo",
                    "url": "https://www.anwo.cl/",
                },
            ],
            "service_focus_points": [
                {
                    "title": "Ingeniería aplicada",
                    "description": "Levantamiento, criterio técnico y solución según el recinto.",
                },
                {
                    "title": "Montaje y ejecución",
                    "description": "Instalación, coordinación en obra y puesta en marcha.",
                },
                {
                    "title": "Mantención y continuidad",
                    "description": "Soporte, diagnóstico y respuesta para operación sostenida.",
                },
            ],
            "company_profile_points": [
                {
                    "title": "Empresa formal",
                    "description": "MAX SERVICES SpA, operación iniciada en 2011.",
                },
                {
                    "title": "Base de trabajo",
                    "description": "Climatización, ventilación, mantención y ejecución en terreno.",
                },
                {
                    "title": "Tipo de cliente",
                    "description": "Constructoras, instituciones, comercio, oficinas y edificios.",
                },
            ],
            "project_method_points": [
                "Tipo de trabajo y especialidad",
                "Sector y clase de cliente",
                "Ubicación general y referencia",
            ],
            "featured_project_types": [
                "Climatización y aire acondicionado",
                "Ventilación e inyección de aire",
                "Extracción para baños, cocinas y subterráneos",
                "Presurización de caja de escaleras",
                "Mantención preventiva y correctiva",
                "Reparación de sistemas y proyectos de clima",
            ],
        },
    )


def location_cities_api(request):
    region = request.GET.get("region", "")
    choices = get_city_choices(region)
    return JsonResponse(
        {
            "results": [{"value": value, "label": label} for value, label in choices],
        }
    )


def location_communes_api(request):
    region = request.GET.get("region", "")
    city = request.GET.get("city", "")
    choices = get_commune_choices(region, city)
    return JsonResponse(
        {
            "results": [
                {"value": value, "label": label}
                for value, label in choices
            ],
        }
    )


def robots_txt(request):
    content = "\n".join(
        [
            "User-agent: *",
            "Disallow: /admin/",
            f"Sitemap: {settings.SITE_URL}/sitemap.xml",
            "",
        ]
    )
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    parsed_site_url = urlparse(settings.SITE_URL)
    protocol = parsed_site_url.scheme or "https"
    domain = parsed_site_url.netloc
    sitemap = StaticViewSitemap()
    urls = sitemap.get_urls(
        page=1,
        site=SitemapSite(domain),
        protocol=protocol,
    )
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in urls:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{escape(url['location'])}</loc>",
                f"    <changefreq>{escape(url['changefreq'])}</changefreq>",
                f"    <priority>{url['priority']}</priority>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    return HttpResponse("\n".join(lines), content_type="application/xml")
