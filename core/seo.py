import json

from django.conf import settings
from django.templatetags.static import static


# Identificadores de la entidad. Con un @id fijo, el Service de cada pagina, las
# fichas de proyecto y el sitio apuntan a LA MISMA empresa, en vez de declarar
# cada uno una empresa suelta que Google tiene que adivinar si es la misma.
ID_EMPRESA = f"{settings.SITE_URL}/#empresa"
ID_SITIO = f"{settings.SITE_URL}/#sitio"

# 07-10-2026: "max service" (sin la s) rankea en la posicion 17,8 y la compiten
# maxservice.cl (ropa de trabajo) y HBO Max. Todas las formas en que se escribe la
# marca van declaradas para que Google las asocie a esta empresa y no a otra.
NOMBRE_EMPRESA = "MAX SERVICES SpA"
NOMBRES_ALTERNATIVOS = ["Max Services SpA", "Max Services", "MAX SERVICES SPA", "maxservices", "maxservicesspa"]


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
            "@type": "HVACBusiness",
            "@id": ID_EMPRESA,
            "name": NOMBRE_EMPRESA,
            "url": settings.SITE_URL,
            "telephone": "+56225590108",
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


def schema_sitio():
    """WebSite: le dice a Google con que nombre mostrar el sitio en resultados.

    Va solo en la home, que es donde Google lo lee. Sin esto el resultado puede
    salir con "maxservicesspa.cl" en vez del nombre de la empresa.
    """
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": ID_SITIO,
        "url": f"{settings.SITE_URL}/",
        "name": "Max Services SpA",
        "alternateName": [n for n in NOMBRES_ALTERNATIVOS if n != "Max Services SpA"],
        "inLanguage": "es-CL",
        "publisher": {"@id": ID_EMPRESA},
    }


def schema_lista_proyectos(proyectos, nombre):
    """ItemList con las fichas de proyecto enlazadas desde la pagina.

    Solo lista fichas que la pagina realmente muestra como enlace.
    """
    if not proyectos:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": nombre,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "url": url_absoluta(f"/proyectos/{p['slug']}/"),
                "name": p["name"],
            }
            for i, p in enumerate(proyectos, start=1)
        ],
    }
