import json

from django.conf import settings
from django.templatetags.static import static


def absolute_static_url(path):
    return f"{settings.SITE_URL}{static(path)}"


def url_absoluta(ruta):
    return f"{settings.SITE_URL}{ruta}"


def schema_json(*bloques):
    """Junta varios bloques de datos estructurados en un solo script.

    Google lee igual de bien un @graph que varios <script> sueltos, y asi la
    plantilla no tiene que repetir el bloque por cada tipo.
    """
    utiles = [b for b in bloques if b]
    if not utiles:
        return ""
    dato = utiles[0] if len(utiles) == 1 else {"@context": "https://schema.org", "@graph": utiles}
    return json.dumps(dato, ensure_ascii=False)


def migas(items):
    """BreadcrumbList: le dice a Google donde vive cada pagina dentro del sitio.

    `items` son pares (nombre, ruta). Tambien alimenta las migas visibles, para
    que lo que ve la persona y lo que lee el buscador sean lo mismo.
    """
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "name": nombre,
                "item": url_absoluta(ruta),
            }
            for i, (nombre, ruta) in enumerate(items, start=1)
        ],
    }


def schema_servicio(servicio, ruta):
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": servicio["nombre"],
        "serviceType": servicio["nombre"],
        "description": servicio["descripcion_seo"],
        "url": url_absoluta(ruta),
        "provider": {
            "@type": "LocalBusiness",
            "name": "MAX SERVICES SPA",
            "url": settings.SITE_URL,
            "telephone": "+56225690108",
            "email": "contacto@maxservicesspa.cl",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Patricio Lynch 9619",
                "addressLocality": "El Bosque",
                "addressRegion": "Región Metropolitana",
                "addressCountry": "CL",
            },
        },
        "areaServed": {
            "@type": "AdministrativeArea",
            "name": "Santiago, Región Metropolitana, Chile",
        },
        "audience": {"@type": "BusinessAudience", "name": "Empresas, edificios e instituciones"},
    }


def schema_preguntas(preguntas):
    """FAQPage con las preguntas reales de cada servicio.

    Solo se declara lo que esta escrito en la pagina: marcar preguntas que el
    visitante no ve es justo lo que Google penaliza.
    """
    if not preguntas:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["p"],
                "acceptedAnswer": {"@type": "Answer", "text": item["r"]},
            }
            for item in preguntas
        ],
    }
