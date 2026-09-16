"""Los seis servicios, cada uno con su propia URL.

Por que existe este archivo: hasta el 16-09-2026 el sitio era UNA sola pagina y
"Servicios", "Empresa" y "Contacto" eran anclas a la misma home. El sitemap
publicaba 2 URLs y Google tenia una sola pagina indexada, asi que el sitio solo
podia aparecer buscando "max services" — su propia marca — y no por lo que la
gente realmente busca ("mantencion aire acondicionado Santiago"). Sin URL propia
no hay donde rankear.

El contenido sale de lo que ya decia la home y de lo que la empresa hace de
verdad. No se inventan certificaciones, plazos, precios ni garantias: si un dato
no estaba antes en el sitio, no se escribe aca.
"""

CIUDAD = "Santiago"

# El orden manda en el menu, en la home y en el sitemap.
SERVICIOS = [
    {
        "slug": "climatizacion-aire-acondicionado",
        "numero": "01",
        "nombre": "Climatización y aire acondicionado",
        "nombre_corto": "Climatización",
        "titulo_seo": "Climatización y aire acondicionado en Santiago | MAX SERVICES",
        "h1": "Climatización y aire acondicionado para empresas en Santiago",
        "descripcion_seo": (
            "Diseño, suministro, montaje y optimización de sistemas de climatización y aire "
            "acondicionado para oficinas, edificios, retail, salud y universidades en Santiago."
        ),
        "resumen": "Diseño, suministro, montaje y optimización de sistemas de climatización.",
        "imagen": "assets/home/hero-main.webp",
        "imagen_alt": "Técnico instalando un equipo de climatización en una oficina corporativa.",
        "entrada": [
            "MAX SERVICES SPA ejecuta proyectos de climatización y aire acondicionado desde 2011, "
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
        "faq": [
            {
                "p": "¿Atienden proyectos de climatización fuera de Santiago?",
                "r": "Sí. La base de operaciones está en Santiago y también se ejecutan proyectos "
                     "en regiones, coordinando el traslado del equipo técnico según el alcance.",
            },
            {
                "p": "¿Trabajan con el equipo que ya tiene instalado la empresa?",
                "r": "Sí. Se puede ampliar, reubicar u optimizar una instalación existente, o "
                     "reemplazar solo las unidades que ya cumplieron su vida útil.",
            },
            {
                "p": "¿Con qué marcas trabajan?",
                "r": "Con marcas reconocidas del rubro y con soluciones compatibles con distintos "
                     "tipos de proyecto. La marca se define según el recinto, el presupuesto y la "
                     "disponibilidad de repuestos.",
            },
        ],
    },
    {
        "slug": "ventilacion-inyeccion-de-aire",
        "numero": "02",
        "nombre": "Ventilación e inyección de aire",
        "nombre_corto": "Ventilación",
        "titulo_seo": "Ventilación e inyección de aire en Santiago | MAX SERVICES",
        "h1": "Sistemas de ventilación e inyección de aire en Santiago",
        "descripcion_seo": (
            "Sistemas de ventilación e inyección de aire para edificios, recintos técnicos y "
            "subterráneos en Santiago. Diseño, montaje y renovación de aire según el proyecto."
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
        "faq": [
            {
                "p": "¿Qué diferencia hay entre ventilación e inyección de aire?",
                "r": "La ventilación renueva el aire de un recinto y la inyección lo introduce de "
                     "forma dirigida a un espacio determinado. En la práctica se diseñan juntas: "
                     "lo que entra tiene que poder salir.",
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
        "titulo_seo": "Extracción de aire para empresas en Santiago | MAX SERVICES",
        "h1": "Sistemas de extracción de aire en Santiago",
        "descripcion_seo": (
            "Diseño, suministro y montaje de sistemas de extracción de aire para baños, cocinas, "
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
        ],
    },
    {
        "slug": "presurizacion-de-escaleras",
        "numero": "04",
        "nombre": "Presurización de caja de escaleras",
        "nombre_corto": "Presurización",
        "titulo_seo": "Presurización de escaleras en edificios | MAX SERVICES",
        "h1": "Presurización de caja de escaleras para edificios en Santiago",
        "descripcion_seo": (
            "Diseño y montaje de sistemas de presurización de caja de escaleras para edificios en "
            "Santiago: seguridad y control de aire en circulaciones protegidas."
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
        ],
    },
    {
        "slug": "mantencion-hvac",
        "numero": "05",
        "nombre": "Mantención preventiva y correctiva",
        "nombre_corto": "Mantención",
        "titulo_seo": "Mantención de aire acondicionado y HVAC en Santiago | MAX SERVICES",
        "h1": "Mantención preventiva y correctiva de sistemas HVAC en Santiago",
        "descripcion_seo": (
            "Mantención preventiva y correctiva de aire acondicionado y sistemas HVAC para "
            "empresas, edificios e instituciones en Santiago."
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
        ],
    },
    {
        "slug": "reparacion-de-sistemas",
        "numero": "06",
        "nombre": "Reparación de sistemas",
        "nombre_corto": "Reparación",
        "titulo_seo": "Reparación de aire acondicionado y HVAC | MAX SERVICES",
        "h1": "Reparación de sistemas de climatización y ventilación en Santiago",
        "descripcion_seo": (
            "Diagnóstico de fallas, ajustes técnicos y recuperación de operación en sistemas de "
            "climatización, ventilación y extracción para empresas en Santiago."
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
