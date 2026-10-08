"""Los seis servicios, cada uno con su propia URL.

Por que existe este archivo: hasta el 16-09-2026 el sitio era UNA sola pagina y
"Servicios", "Empresa" y "Contacto" eran anclas a la misma home. El sitemap
publicaba 2 URLs y Google tenia una sola pagina indexada, asi que el sitio solo
podia aparecer buscando "max services" — su propia marca — y no por lo que la
gente realmente busca ("mantencion aire acondicionado Santiago"). Sin URL propia
no hay donde rankear.

07-10-2026: con Search Console a 28 dias, los seis servicios estaban en la
pagina 2 de Google (posiciones 10 a 23). Cada uno paso a tener un title que
cabe entero (60 caracteres), una description que no se corta (155), secciones
que responden la busqueda concreta y los proyectos reales donde se aplico.

El contenido sale de lo que ya decia el sitio y de lo que la empresa hace de
verdad: las referencias y clientes estan publicados en la home y en las fichas
de proyecto, y las marcas en "Marcas y proveedores". No se inventan
certificaciones, normas, plazos, precios, garantias ni comunas: si un dato no
estaba antes en el sitio, no se escribe aca.
"""

CIUDAD = "Santiago"

# Las marcas que la home ya publica en "Marcas y proveedores".
MARCAS_PUBLICADAS = "CLARK, LG, GREE, Bravo Aires, Frigair, ANWO y S&P"

# El orden manda en el menu, en la home y en el sitemap.
#
# `etiquetas_proyectos` son los valores de `services` de cada proyecto en
# portfolio/catalog.py: con eso cada servicio enlaza a las obras reales donde se
# aplico, y cada ficha de proyecto queda enlazada desde al menos un servicio.
SERVICIOS = [
    {
        "slug": "climatizacion-aire-acondicionado",
        "numero": "01",
        "nombre": "Climatización y aire acondicionado",
        "nombre_corto": "Climatización",
        "titulo_seo": "Climatización y aire acondicionado, Santiago | Max Services",
        "h1": "Climatización y aire acondicionado para empresas en Santiago",
        "descripcion_seo": (
            "Diseño, suministro y montaje de climatización y aire acondicionado para oficinas, "
            "edificios, retail, salud y universidades en Santiago, desde 2011."
        ),
        "resumen": "Diseño, suministro, montaje y optimización de sistemas de climatización.",
        "imagen": "assets/home/hero-main.webp",
        "imagen_alt": "Técnico instalando un equipo de climatización en una oficina corporativa.",
        "entrada": [
            "MAX SERVICES SpA ejecuta proyectos de climatización y aire acondicionado desde 2011, "
            "en Santiago y en regiones. El trabajo parte por entender el recinto: cuánta gente lo "
            "usa, qué equipos disipan calor y qué horario tiene que cubrir el sistema.",
            "Con eso se define el equipamiento, el trazado de ductos y los puntos de suministro, "
            "y se ejecuta el montaje coordinado con el resto de la obra o con la operación del "
            "cliente si el recinto está funcionando.",
        ],
        "incluye": [
            "Evaluación técnica en terreno del recinto y de su uso real",
            "Definición de equipos y capacidad según carga térmica y horario de operación",
            "Suministro de equipos de marcas con presencia habitual en el mercado nacional",
            "Montaje de unidades, ductos, drenajes y conexiones eléctricas",
            "Puesta en marcha, pruebas de funcionamiento y entrega al cliente",
        ],
        "aplica": [
            "Oficinas y edificios corporativos",
            "Retail y locales comerciales",
            "Recintos de salud",
            "Universidades e instituciones educativas",
        ],
        "secciones": [
            {
                "h2": "Aire acondicionado para empresas, no para un dormitorio",
                "parrafos": [
                    "Un recinto de trabajo no se climatiza como una casa. Una oficina con mucha "
                    "gente, una sala con equipos encendidos todo el día o un local de retail con "
                    "flujo constante cargan calor de forma distinta, y el sistema se dimensiona "
                    "según esa carga y según el horario que tiene que cubrir.",
                    "Por eso la evaluación se hace en terreno y sobre el uso real del recinto, y "
                    "no a partir de los metros cuadrados solamente.",
                ],
            },
            {
                "h2": "Instalación nueva o una que ya existe",
                "parrafos": [
                    "Se ejecutan proyectos de obra nueva, coordinados con la constructora, y "
                    "también trabajos sobre instalaciones en funcionamiento: ampliar, reubicar u "
                    "optimizar un sistema, o reemplazar solo las unidades que ya cumplieron su "
                    "vida útil, coordinando con la operación del cliente.",
                ],
            },
            {
                "h2": "Experiencia en salud, universidades, retail y oficinas",
                "parrafos": [
                    "Entre las referencias de climatización están el Hospital Luis Calvo "
                    "Mackenna, la Universidad Diego Portales, la Universidad Autónoma de Chile en "
                    "Temuco y Talca, las oficinas de Inverko y la remodelación del Hiper Líder "
                    "Departamental. Cada una tiene su ficha en la sección de proyectos.",
                ],
            },
        ],
        "etiquetas_proyectos": ["Climatización"],
        "titulo_proyectos": "Proyectos de climatización ejecutados",
        "faq": [
            {
                "p": "¿Atienden proyectos de climatización fuera de Santiago?",
                "r": "Sí. La base de operaciones está en Santiago y también se ejecutan proyectos "
                     "en regiones, coordinando el traslado del equipo técnico según el alcance. "
                     "Un ejemplo es la Universidad Autónoma de Chile, en Temuco y Talca.",
            },
            {
                "p": "¿Trabajan con el equipo que ya tiene instalado la empresa?",
                "r": "Sí. Se puede ampliar, reubicar u optimizar una instalación existente, o "
                     "reemplazar solo las unidades que ya cumplieron su vida útil.",
            },
            {
                "p": "¿Con qué marcas trabajan?",
                "r": f"Con marcas reconocidas del rubro, entre ellas {MARCAS_PUBLICADAS}. La "
                     "marca se define según el recinto, el presupuesto y la disponibilidad de "
                     "repuestos.",
            },
            {
                "p": "¿También hacen la mantención del aire acondicionado después de instalarlo?",
                "r": "Sí. La mantención preventiva y correctiva es un servicio propio y se puede "
                     "contratar para equipos instalados por MAX SERVICES o por otra empresa.",
            },
        ],
    },
    {
        "slug": "ventilacion-inyeccion-de-aire",
        "numero": "02",
        "nombre": "Ventilación e inyección de aire",
        "nombre_corto": "Ventilación",
        "titulo_seo": "Ventilación e inyección de aire en Santiago | Max Services",
        "h1": "Ventilación, inyección y retorno de aire en Santiago",
        "descripcion_seo": (
            "Sistemas de ventilación, inyección y retorno de aire para edificios, "
            "subterráneos y salas técnicas en Santiago. Diseño de caudales, ductos y montaje."
        ),
        "resumen": "Sistemas de ventilación e inyección definidos según el proyecto.",
        "imagen": "assets/home/experience-support.webp",
        "imagen_alt": "Instalación de ductos de ventilación en un recinto corporativo.",
        "entrada": [
            "La ventilación mecánica renueva el aire de recintos que no pueden depender de puertas "
            "y ventanas: subterráneos, salas técnicas, bodegas y espacios interiores de edificios.",
            "MAX SERVICES define el caudal necesario para cada recinto, el trazado de ductos y los "
            "equipos que lo mueven, y ejecuta el montaje coordinado con las demás especialidades "
            "de la obra.",
        ],
        "incluye": [
            "Definición del caudal de aire según el uso y la normativa aplicable al recinto",
            "Diseño del trazado de ductos y de los puntos de inyección",
            "Suministro y montaje de ventiladores, ductos y rejillas",
            "Coordinación con las otras especialidades de la obra",
            "Pruebas de funcionamiento y entrega",
        ],
        "aplica": [
            "Subterráneos y estacionamientos",
            "Salas técnicas y recintos de equipos",
            "Edificios corporativos y habitacionales",
            "Bodegas y zonas de operación",
        ],
        "secciones": [
            {
                "h2": "Inyección y retorno de aire: por qué se diseñan juntos",
                "parrafos": [
                    "La inyección introduce aire de forma dirigida a un recinto y el retorno o la "
                    "extracción lo saca. Si solo se diseña la mitad, el aire no circula: lo que "
                    "entra tiene que tener por dónde salir.",
                    "Por eso el proyecto define los dos recorridos a la vez, con sus caudales, "
                    "sus ductos y la ubicación de rejillas y equipos.",
                ],
            },
            {
                "h2": "Ventilación en obra nueva y en edificios en uso",
                "parrafos": [
                    "En obra nueva, el montaje avanza coordinado con la constructora desde las "
                    "etapas tempranas, como en las obras de Echeverría Izquierdo y TASCO Boetsch. "
                    "En un edificio ya construido, el trazado se adapta al espacio disponible "
                    "para ductos y equipos, que se revisa en terreno antes de proponer la solución.",
                ],
            },
        ],
        "etiquetas_proyectos": ["Ventilación"],
        "titulo_proyectos": "Proyectos de ventilación ejecutados",
        "faq": [
            {
                "p": "¿Qué diferencia hay entre ventilación e inyección de aire?",
                "r": "La ventilación renueva el aire de un recinto y la inyección lo introduce de "
                     "forma dirigida a un espacio determinado. En la práctica se diseñan juntas: "
                     "lo que entra tiene que poder salir.",
            },
            {
                "p": "¿Qué es el retorno de aire?",
                "r": "Es el recorrido por el que el aire sale del recinto después de ser inyectado, "
                     "ya sea de vuelta al sistema o hacia el exterior. Se diseña junto con la "
                     "inyección para que el aire realmente circule.",
            },
            {
                "p": "¿Se puede instalar en un edificio ya construido?",
                "r": "Sí, evaluando en terreno el espacio disponible para ductos y equipos. El "
                     "trazado se adapta a lo que el recinto permite.",
            },
        ],
    },
    {
        "slug": "extraccion-de-aire",
        "numero": "03",
        "nombre": "Extracción de aire",
        "nombre_corto": "Extracción",
        "titulo_seo": "Sistemas de extracción de aire en Santiago | Max Services",
        "h1": "Sistemas de extracción de aire para cocinas, baños y subterráneos",
        "descripcion_seo": (
            "Diseño, montaje y mantención de sistemas de extracción de aire para cocinas, baños, "
            "subterráneos y zonas de operación exigente en Santiago y regiones."
        ),
        "resumen": "Diseño, suministro y montaje de sistemas de extracción para distintos recintos.",
        "imagen": "assets/home/about-company.webp",
        "imagen_alt": "Sistema de extracción de aire montado en un recinto industrial.",
        "entrada": [
            "La extracción saca del recinto el aire cargado de humedad, olores, humo o calor. En "
            "cocinas, baños y subterráneos no es un tema de confort: es lo que permite que el "
            "espacio se pueda usar.",
            "Cada sistema se dimensiona según lo que hay que extraer y desde dónde, y el montaje "
            "considera el recorrido completo hasta la descarga al exterior.",
        ],
        "incluye": [
            "Evaluación del recinto y de la carga que debe extraerse",
            "Diseño del sistema y del recorrido hasta la descarga",
            "Suministro y montaje de campanas, ductos y extractores",
            "Conexiones eléctricas y de control del sistema",
            "Pruebas de funcionamiento y entrega",
        ],
        "aplica": [
            "Cocinas industriales y casinos",
            "Baños y recintos húmedos",
            "Subterráneos y estacionamientos",
            "Zonas de producción y operación exigente",
        ],
        "secciones": [
            {
                "h2": "Extracción para cocinas, baños y subterráneos",
                "parrafos": [
                    "En una cocina industrial o un casino la extracción parte en la campana y "
                    "termina en la descarga al exterior; en un baño o un subterráneo, lo que manda "
                    "es la humedad y la renovación del aire. Cada caso se dimensiona según lo que "
                    "hay que sacar y desde dónde.",
                ],
            },
            {
                "h2": "Cuando el sistema de extracción quedó corto",
                "parrafos": [
                    "Si el recinto sigue con olor, humo o humedad, el problema puede estar en el "
                    "equipo, en el trazado o en la descarga. Se revisa en terreno qué está "
                    "limitando el sistema y se propone la corrección concreta.",
                    "También se renuevan instalaciones antiguas: en un edificio patrimonial de "
                    "ladrillo se reemplazaron equipos obsoletos por nuevos sistemas de "
                    "ventilación y extracción, con mínima intervención en la estructura.",
                ],
            },
            {
                "h2": "Mantención de sistemas de extracción y ventilación",
                "parrafos": [
                    "Un extractor que trabaja todos los días necesita revisión programada, igual "
                    "que un equipo de aire acondicionado. La mantención preventiva y correctiva "
                    "de MAX SERVICES incluye los sistemas de extracción y ventilación.",
                ],
            },
        ],
        "etiquetas_proyectos": ["Extracción"],
        "titulo_proyectos": "Proyectos de extracción ejecutados",
        "faq": [
            {
                "p": "¿Hacen extracción para cocinas de casinos y restaurantes?",
                "r": "Sí. Es uno de los recintos donde más se aplica, incluyendo campana, ductos y "
                     "el recorrido hasta la descarga al exterior.",
            },
            {
                "p": "¿Pueden mejorar un sistema de extracción que quedó corto?",
                "r": "Sí. Se evalúa en terreno qué está limitando el sistema —equipo, trazado o "
                     "descarga— y se propone la corrección concreta.",
            },
            {
                "p": "¿Hacen mantención de sistemas de extracción y ventilación?",
                "r": "Sí. Se atienden dentro de la mantención preventiva y correctiva, con un plan "
                     "que se define según el uso y el estado de la instalación.",
            },
        ],
    },
    {
        "slug": "presurizacion-de-escaleras",
        "numero": "04",
        "nombre": "Presurización de caja de escaleras",
        "nombre_corto": "Presurización",
        "titulo_seo": "Presurización de escaleras en Santiago | Max Services",
        "h1": "Presurización de caja de escaleras para edificios en Santiago",
        "descripcion_seo": (
            "Presurización de escaleras para edificios en Santiago: diseño, montaje y pruebas del "
            "sistema que mantiene el humo fuera de la vía de evacuación."
        ),
        "resumen": "Diseño y montaje de sistemas para seguridad y control de aire en edificios.",
        "imagen": "assets/home/contact-evaluation.webp",
        "imagen_alt": "Equipo de presurización instalado en la caja de escaleras de un edificio.",
        "entrada": [
            "La presurización mantiene la caja de escaleras con mayor presión que el resto del "
            "edificio, para que el humo no entre en la vía de evacuación durante un incendio.",
            "Es un sistema que se diseña junto con la arquitectura del edificio y que se ejecuta "
            "coordinado con la obra: equipo, ductos, rejillas y el control que lo activa.",
        ],
        "incluye": [
            "Definición del sistema según la geometría de la caja de escaleras",
            "Suministro y montaje del equipo de presurización",
            "Ductos, rejillas y elementos de descarga",
            "Conexión del sistema de control y activación",
            "Pruebas de funcionamiento y entrega",
        ],
        "aplica": [
            "Edificios habitacionales en altura",
            "Edificios corporativos y de oficinas",
            "Circulaciones protegidas y recintos de apoyo",
        ],
        "secciones": [
            {
                "h2": "Cómo funciona la presurización de escaleras",
                "parrafos": [
                    "El equipo inyecta aire a la caja de escaleras y la deja con más presión que "
                    "los pisos. Cuando se abre una puerta, el aire sale desde la escalera hacia "
                    "el piso y no al revés, así que el humo de un incendio no entra en la vía por "
                    "la que la gente evacúa.",
                    "El sistema se activa con su propio control y tiene que funcionar cuando se "
                    "necesita; por eso la entrega incluye pruebas de funcionamiento.",
                ],
            },
            {
                "h2": "Presurización en obra, coordinada con la constructora",
                "parrafos": [
                    "Buena parte de estos proyectos se ejecuta directamente con constructoras e "
                    "inmobiliarias: TASCO Boetsch, Echeverría Izquierdo e Inmobiliaria La "
                    "Fontana, entre otras. El montaje avanza con la obra para que ductos, "
                    "rejillas y equipo queden listos cuando el edificio se entrega.",
                ],
            },
            {
                "h2": "Edificios ya habitados y comunidades",
                "parrafos": [
                    "En edificios residenciales y comunidades también se trabaja sobre sistemas "
                    "existentes, con presurización, ventilación y mantención para que el sistema "
                    "siga respondiendo con el paso de los años.",
                ],
            },
        ],
        "etiquetas_proyectos": ["Presurización"],
        "titulo_proyectos": "Obras con presurización de escaleras",
        "faq": [
            {
                "p": "¿En qué edificios se exige presurización de escaleras?",
                "r": "Depende de la altura y del tipo de edificio según la normativa vigente y de "
                     "lo que defina el proyecto de arquitectura. La revisión se hace caso a caso "
                     "sobre los planos del edificio.",
            },
            {
                "p": "¿Trabajan coordinados con la constructora?",
                "r": "Sí. Buena parte de los proyectos se ejecuta directamente con constructoras e "
                     "inmobiliarias, coordinando plazos con el resto de las especialidades.",
            },
            {
                "p": "¿El sistema se prueba antes de entregarlo?",
                "r": "Sí. La entrega incluye las pruebas de funcionamiento del equipo y de su "
                     "sistema de control y activación.",
            },
            {
                "p": "¿Hacen mantención a sistemas de presurización ya instalados?",
                "r": "Sí, en edificios residenciales y comunidades, dentro de la mantención de "
                     "sistemas HVAC.",
            },
        ],
    },
    {
        "slug": "mantencion-hvac",
        "numero": "05",
        "nombre": "Mantención preventiva y correctiva",
        "nombre_corto": "Mantención",
        "titulo_seo": "Mantención de aire acondicionado en Santiago | Max Services",
        "h1": "Mantención de aire acondicionado y sistemas HVAC en Santiago",
        "descripcion_seo": (
            "Mantención preventiva y correctiva de aire acondicionado, ventilación y extracción "
            "para empresas, edificios, comunidades e instituciones en Santiago."
        ),
        "resumen": "Mantención de sistemas HVAC según uso, criticidad y estado de la instalación.",
        "imagen": "assets/home/experience-support.webp",
        "imagen_alt": "Técnico realizando mantención a un equipo de climatización.",
        "entrada": [
            "Un equipo de climatización sin mantención consume más, enfría menos y falla cuando "
            "más se ocupa. La mantención preventiva evita esa curva: revisión programada, limpieza "
            "y ajustes antes de que el equipo se detenga.",
            "El plan se arma según el uso real de cada instalación, qué tan crítica es para la "
            "operación y en qué estado está hoy. La mantención correctiva atiende lo que ya falló.",
        ],
        "incluye": [
            "Revisión programada de los equipos según su uso y criticidad",
            "Limpieza de filtros y componentes, y ajustes de funcionamiento",
            "Detección temprana de fallas antes de que detengan la operación",
            "Atención correctiva cuando el equipo ya presenta una falla",
            "Registro de lo realizado en cada visita",
        ],
        "aplica": [
            "Oficinas y edificios corporativos",
            "Retail y locales comerciales",
            "Recintos de salud y universidades",
            "Comunidades y administraciones de edificios",
        ],
        "secciones": [
            {
                "h2": "Mantención preventiva: qué se revisa en cada visita",
                "parrafos": [
                    "La visita programada revisa el funcionamiento de cada equipo, limpia filtros "
                    "y componentes y ajusta lo que se desvió. Lo que importa es encontrar la falla "
                    "cuando todavía es un ajuste y no una detención, y dejar registro de lo "
                    "realizado para que el historial de la instalación no dependa de la memoria.",
                ],
            },
            {
                "h2": "Mantención correctiva cuando el equipo ya falló",
                "parrafos": [
                    "Cuando un equipo se detuvo o perdió rendimiento, se diagnostica en terreno y "
                    "se corrige. Si la falla se repite o el equipo ya no se justifica, se "
                    "recomienda qué conviene hacer con él.",
                ],
            },
            {
                "h2": "Mantención de sistemas de extracción y ventilación",
                "parrafos": [
                    "La mantención no se limita al aire acondicionado: también cubre los sistemas "
                    "de ventilación, extracción y presurización de edificios, que trabajan todo el "
                    "año y suelen revisarse solo cuando fallan.",
                ],
            },
        ],
        "etiquetas_proyectos": ["Mantención"],
        "titulo_proyectos": "Proyectos con mantención",
        "faq": [
            {
                "p": "¿Cada cuánto se debe hacer mantención a un aire acondicionado?",
                "r": "Depende de cuántas horas funciona el equipo y del ambiente donde está "
                     "instalado. Un recinto con mucho uso o mucho polvo necesita visitas más "
                     "seguidas que una oficina de uso parcial; la frecuencia se define al evaluar "
                     "la instalación.",
            },
            {
                "p": "¿Atienden mantención de equipos que instaló otra empresa?",
                "r": "Sí. Se revisa el estado actual de la instalación y, a partir de eso, se "
                     "propone el plan de mantención.",
            },
            {
                "p": "¿Hacen mantención para comunidades y administraciones de edificios?",
                "r": "Sí, además de empresas e instituciones. El plan se ajusta al tipo de recinto "
                     "y a los horarios en que se puede intervenir.",
            },
            {
                "p": "¿La mantención incluye los sistemas de extracción y ventilación?",
                "r": "Sí. El plan puede considerar el aire acondicionado y también la ventilación, "
                     "la extracción y la presurización del edificio.",
            },
        ],
    },
    {
        "slug": "reparacion-de-sistemas",
        "numero": "06",
        "nombre": "Reparación de sistemas",
        "nombre_corto": "Reparación",
        "titulo_seo": "Reparación de aire acondicionado en Santiago | Max Services",
        "h1": "Reparación de sistemas de climatización y ventilación en Santiago",
        "descripcion_seo": (
            "Diagnóstico de fallas y reparación de aire acondicionado, ventilación y extracción "
            "para empresas en Santiago, con recomendación escrita de qué conviene."
        ),
        "resumen": "Diagnóstico de fallas, ajustes técnicos y recuperación de operación.",
        "imagen": "assets/home/contact-evaluation.webp",
        "imagen_alt": "Técnico diagnosticando la falla de un equipo de climatización en terreno.",
        "entrada": [
            "Cuando un sistema se detiene, lo primero es saber por qué. El diagnóstico en terreno "
            "separa la falla real de sus síntomas: no siempre el equipo que se apagó es el que "
            "tiene el problema.",
            "A partir del diagnóstico se ejecuta la reparación y, si corresponde, se propone la "
            "mejora que evita que vuelva a ocurrir.",
        ],
        "incluye": [
            "Diagnóstico de la falla en terreno",
            "Reparación o recambio de los componentes afectados",
            "Ajustes de funcionamiento del sistema",
            "Recomendaciones para evitar que la falla se repita",
            "Pruebas de funcionamiento antes de entregar",
        ],
        "aplica": [
            "Equipos de climatización detenidos o con bajo rendimiento",
            "Sistemas de ventilación y extracción con fallas",
            "Instalaciones que requieren recuperar continuidad operativa",
        ],
        "secciones": [
            {
                "h2": "Reparar o reemplazar: se decide después del diagnóstico",
                "parrafos": [
                    "No siempre conviene reparar. Después del diagnóstico se compara el costo de "
                    "la reparación con la vida útil que le queda al equipo, y esa recomendación "
                    "se entrega por escrito junto con la evaluación.",
                ],
            },
        ],
        "etiquetas_proyectos": ["Mantención"],
        "titulo_proyectos": "Instalaciones con mantención y soporte técnico",
        "faq": [
            {
                "p": "¿Reparan equipos de cualquier marca?",
                "r": "Se trabaja con marcas reconocidas del rubro y con soluciones compatibles con "
                     "distintos tipos de proyecto. La viabilidad de la reparación depende del "
                     "estado del equipo y de la disponibilidad de repuestos.",
            },
            {
                "p": "¿Conviene reparar o reemplazar el equipo?",
                "r": "Se responde después del diagnóstico, comparando el costo de la reparación "
                     "con la vida útil que le queda al equipo. Esa recomendación se entrega por "
                     "escrito junto con la evaluación.",
            },
        ],
    },
]

POR_SLUG = {s["slug"]: s for s in SERVICIOS}


def con_relacionados(servicio):
    """Los otros servicios, para enlazar entre paginas.

    El enlace interno es lo que reparte autoridad entre las paginas nuevas: sin
    esto cada servicio queda aislado y Google lo trata como una hoja suelta.
    """
    return [s for s in SERVICIOS if s["slug"] != servicio["slug"]]


def proyectos_del_servicio(servicio, proyectos):
    """Las fichas de proyecto donde se aplico este servicio.

    07-10-2026: 15 de las 16 fichas estaban "Descubierta, actualmente sin
    indexar" en Search Console. Las enlazaba solo /proyectos/; ningun servicio
    apuntaba a ellas, asi que Google las veia como paginas sin importancia.
    Primero van las obras terminadas y en ejecucion (fotos propias), despues las
    referencias.
    """
    etiquetas = set(servicio.get("etiquetas_proyectos", []))
    elegidos = [p for p in proyectos if etiquetas & set(p.get("services", []))]
    orden = {"terminado": 0, "en-ejecucion": 1}
    return sorted(elegidos, key=lambda p: orden.get(p.get("category"), 2))


def servicios_del_proyecto(proyecto):
    """Los servicios cuya pagina corresponde a lo que se hizo en el proyecto.

    Reparacion comparte la etiqueta "Mantención" para mostrar proyectos, pero una
    ficha de proyecto no la ofrece como "servicio aplicado": nadie la registro asi.
    """
    aplicados = set(proyecto.get("services", []))
    return [
        s for s in SERVICIOS
        if aplicados & set(s.get("etiquetas_proyectos", []))
        and s["slug"] != "reparacion-de-sistemas"
    ]
