import json

from django.conf import settings

from core.seo import absolute_static_url


def site_meta(request):
    local_business_schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "MAX SERVICES SPA",
        "description": "Empresa de climatización, ventilación y proyectos HVAC en Santiago, Región Metropolitana, Chile.",
        "url": settings.SITE_URL,
        "email": "contacto@maxservicesspa.cl",
        "areaServed": {
            "@type": "AdministrativeArea",
            "name": "Santiago, Región Metropolitana, Chile",
        },
        "knowsAbout": [
            "Climatización",
            "Ventilación",
            "Extracción de aire",
            "Presurización",
            "Inyección de aire",
            "Mantención HVAC",
            "Proyectos HVAC",
        ],
    }

    return {
        "site_url": settings.SITE_URL,
        "default_og_image": absolute_static_url("assets/home/hero-main.png"),
        "favicon_image": "assets/brand/max-services-symbol-real-v2.png",
        "local_business_schema_json": json.dumps(
            local_business_schema,
            ensure_ascii=False,
        ),
        "company_name": "MAX SERVICES SpA",
        "company_short_name": "MAX SERVICES SPA",
        "company_tagline": "Climatización, ventilación y sistemas de aire",
        "company_location": "Santiago y Región Metropolitana",
        "company_address": "Patricio Lynch 9619, El Bosque, Santiago",
        "company_email": "fda@maxservicesspa.cl",
        "company_contact_email": "contacto@maxservicesspa.cl",
        "company_email_secondary": "maxservicesspa@maxservicesspa.cl",
        "company_email_support": "mia@maxservicesspa.cl",
        "company_phone_display": "22 559 01 08",
        "company_phone_href": "tel:+56225690108",
        "company_hours": "Lunes a viernes de 9:00 a 18:30 hrs",
        "company_start_year": "2011",
        "company_start_date": "11 de octubre de 2011",
        "company_rut": "76.174.166-7",
        "company_legal_representative": "Felipe Andrés Dinamarca Abarca",
        "company_website": "www.maxservicesspa.cl",
    }
