import json

from django.conf import settings

from core.seo import absolute_static_url
from core.servicios import SERVICIOS


def site_meta(request):
    # Ficha de la empresa para Google. Lo que estaba antes no traia direccion,
    # telefono ni horario: justo los datos con los que Google arma el panel
    # lateral y decide si el negocio es real y esta cerca de quien busca.
    local_business_schema = {
        "@context": "https://schema.org",
        "@type": "HVACBusiness",
        "name": "MAX SERVICES SPA",
        "legalName": "MAX SERVICES SpA",
        "description": "Empresa de climatización, ventilación y proyectos HVAC en Santiago, Región Metropolitana, Chile.",
        "url": settings.SITE_URL,
        "email": "contacto@maxservicesspa.cl",
        "telephone": "+56225590108",
        "foundingDate": "2011-10-11",
        "image": absolute_static_url("assets/social/og-default.jpg"),
        "logo": absolute_static_url("assets/brand/max-services-symbol-real-v2.png"),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Patricio Lynch 9619",
            "addressLocality": "El Bosque",
            "addressRegion": "Región Metropolitana",
            "addressCountry": "CL",
        },
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "09:00",
                "closes": "18:30",
            }
        ],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Servicios HVAC",
            "itemListElement": [
                {
                    "@type": "Offer",
                    "itemOffered": {
                        "@type": "Service",
                        "name": servicio["nombre"],
                        "url": f"{settings.SITE_URL}/servicios/{servicio['slug']}/",
                    },
                }
                for servicio in SERVICIOS
            ],
        },
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
        # Para el pie: la lista de servicios la necesita cada pagina.
        "servicios_del_sitio": SERVICIOS,
        "ga4_measurement_id": settings.GA4_MEASUREMENT_ID,
        "google_site_verification": settings.GOOGLE_SITE_VERIFICATION,
        "default_og_image": absolute_static_url("assets/social/og-default.jpg"),
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
        "company_phone_href": "tel:+56225590108",
        "company_hours": "Lunes a viernes de 9:00 a 18:30 hrs",
        "company_start_year": "2011",
        "company_start_date": "11 de octubre de 2011",
        "company_rut": "76.174.166-7",
        "company_legal_representative": "Felipe Andrés Dinamarca Abarca",
        "company_website": "www.maxservicesspa.cl",
    }
