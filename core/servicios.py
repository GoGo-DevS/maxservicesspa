"""Los siete servicios, cada uno con su propia URL.

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
        "tarjeta": "Aplicación en oficinas, edificios, retail, salud y universidades.",
        "servicio_formulario": "climatizacion",
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
        # 03-11-2026: Search Console trae a esta pagina "inyeccion de aire" (pos 9,2),
        # "inyección de aire" (7,5), "extraccion e inyeccion de aire" (7) e
        # "inyeccion y extraccion de aire" (3). En el autocompletado la frase que
        # se repite es "inyección y extracción de aire" (sistema, equipos,
        # ductos, rejillas). El title y el H1 la dicen tal cual.
        "titulo_seo": "Ventilación, inyección y extracción de aire | Max Services",
        "h1": "Ventilación, inyección y extracción de aire en Santiago",
        "descripcion_seo": (
            "Sistemas de inyección y extracción de aire para edificios, subterráneos, cocinas "
            "y salas técnicas en Santiago: caudales, ductos, rejillas y montaje."
        ),
        "resumen": "Sistemas de ventilación e inyección definidos según el proyecto.",
        "tarjeta": "Renovación de aire en recintos técnicos, edificios y subterráneos.",
        "servicio_formulario": "ventilacion",
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
            "Diseño del trazado de ductos y de los puntos de inyección y extracción",
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
                # "que es la inyeccion de aire", "inyeccion de aire fresco / exterior",
                # "sistema de inyeccion de aire": autocompletado 03-11-2026.
                "h2": "Qué es la inyección de aire",
                "parrafos": [
                    "La inyección de aire lleva aire exterior al interior de un recinto: un "
                    "ventilador lo impulsa por una red de ductos y lo reparte con rejillas o "
                    "difusores en los puntos donde se necesita.",
                    "Es la mitad de un sistema de ventilación. La otra mitad es la extracción o el "
                    "retorno, que saca el aire ya usado; por eso se habla de sistemas de inyección "
                    "y extracción de aire. En una cocina industrial, por ejemplo, la inyección "
                    "repone el aire que saca la campana.",
                ],
                "enlace": {
                    "slug": "extraccion-cocinas-industriales",
                    "texto": "Extracción e inyección de aire en cocinas industriales",
                },
            },
            {
                "h2": "Inyección, extracción y retorno: por qué se diseñan juntos",
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
                "p": "¿Qué es un sistema de inyección y extracción de aire?",
                "r": "Es un sistema que introduce aire exterior al recinto y saca el aire usado, "
                     "cada recorrido con sus ductos, rejillas y equipos. Se diseñan juntos para "
                     "que el aire realmente circule.",
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
        # 03-11-2026: el H1 decia "para cocinas, baños y subterráneos" y competia con
        # /extraccion-cocinas-industriales/ por la misma busqueda. Las cocinas van en
        # su pagina; esta toma "extracción de aire en edificios / baños / sótanos /
        # estacionamientos" (autocompletado) y enlaza a la de cocinas.
        "h1": "Sistemas de extracción de aire para edificios, baños y subterráneos",
        "descripcion_seo": (
            "Diseño, montaje y mantención de sistemas de extracción de aire para edificios, "
            "baños, subterráneos y estacionamientos en Santiago y regiones."
        ),
        "resumen": "Diseño, suministro y montaje de sistemas de extracción para distintos recintos.",
        "tarjeta": "Baños, subterráneos, estacionamientos y zonas de operación exigente.",
        "servicio_formulario": "extraccion",
        "imagen": "assets/home/about-company.webp",
        # La foto muestra al equipo con planos, no un sistema montado.
        "imagen_alt": "Técnicos de MAX SERVICES revisando planos junto a un tablero eléctrico.",
        "entrada": [
            "La extracción saca del recinto el aire cargado de humedad, olores, humo o calor. En "
            "baños, subterráneos y estacionamientos no es un tema de confort: es lo que permite "
            "que el espacio se pueda usar.",
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
                "h2": "Extracción para baños, subterráneos y estacionamientos",
                "parrafos": [
                    "En un baño o un recinto húmedo lo que manda es la humedad. En un subterráneo o "
                    "un estacionamiento, la renovación de un aire que no tiene salida natural y "
                    "que acumula los gases de los vehículos. Cada caso se dimensiona según lo que "
                    "hay que sacar y desde dónde.",
                    "Las cocinas industriales y los casinos tienen su propio recorrido, que parte "
                    "en la campana y necesita reponer el aire que saca: tienen su página aparte.",
                ],
                "enlace": {
                    "slug": "extraccion-cocinas-industriales",
                    "texto": "Extracción de aire en cocinas industriales y casinos",
                },
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
        # 16-10-2026: "extracción cocina industrial" es una de las búsquedas que
        # trae al cliente que contrata (salió de una agencia de Ads que le
        # escribió a Max), y el sitio la nombraba UNA vez, dentro de la página
        # general de extracción.
        #
        # 03-11-2026: la URL Inspection de Search Console la daba "Descubierta:
        # actualmente sin indexar" (Google nunca la rastreó). El 70 % de su texto
        # visible ya estaba en /extraccion-de-aire/: mismos párrafos, misma foto,
        # mismos proyectos, y el H1 de esa página también decía "cocinas". Se
        # reescribió con lo que busca quien tiene una cocina, según el
        # autocompletado: campana con salida al exterior, inyección de aire en la
        # cocina y por qué una campana industrial no funciona. Nada de precios,
        # normas ni plazos: eso lo confirma Max antes de publicarse.
        "slug": "extraccion-cocinas-industriales",
        "numero": "04",
        "nombre": "Extracción para cocinas industriales",
        "nombre_corto": "Cocinas industriales",
        "titulo_seo": "Extracción de aire en cocinas industriales | Max Services",
        "h1": "Extracción de aire para cocinas industriales y casinos",
        "descripcion_seo": (
            "Campana, ducto, extractor e inyección de aire para cocinas industriales, casinos y "
            "restaurantes en Santiago: diseño, montaje y mantención del sistema."
        ),
        "resumen": "Campana, ducto, extractor e inyección de aire para la cocina.",
        "tarjeta": "Casinos, restaurantes y cocinas de empresas e instituciones.",
        "servicio_formulario": "extraccion",
        "imagen": "assets/home/experience-support.webp",
        "imagen_alt": "Ductos metálicos de aire montados bajo el cielo de un recinto técnico.",
        "entrada": [
            "Una cocina industrial genera humo, grasa, calor y vapor durante todo el turno. La "
            "campana lo capta sobre los equipos de cocción, el ducto lo lleva hasta la descarga "
            "al exterior y la inyección repone el aire que la campana saca.",
            "MAX SERVICES diseña y monta ese sistema completo para casinos, restaurantes y "
            "cocinas de empresas e instituciones, y lo mantiene después de entregarlo.",
        ],
        "incluye": [
            "Evaluación en terreno de los equipos de cocción y de las horas de uso",
            "Campana sobre los equipos, con su salida al exterior",
            "Ducto y extractor dimensionados para el recorrido completo",
            "Inyección de aire de reposición cuando la cocina la necesita",
            "Conexión eléctrica, control y pruebas antes de entregar",
        ],
        "aplica": [
            "Cocinas industriales",
            "Casinos de empresas e instituciones",
            "Cocinas de restaurantes",
        ],
        "secciones": [
            {
                "h2": "Campana, ducto y extractor: un solo recorrido hasta el exterior",
                "parrafos": [
                    "La campana capta lo que sale de la cocción, el ducto lo conduce y el "
                    "extractor lo mueve hasta la descarga al exterior, por el techo o por un muro. "
                    "Las tres partes se dimensionan juntas: una campana grande con un extractor "
                    "que no alcanza deja la cocina igual que antes.",
                    "Por eso la evaluación parte por los equipos que quedan bajo la campana y por "
                    "el camino que puede seguir el ducto dentro del edificio hasta salir.",
                ],
            },
            {
                "h2": "Inyección de aire: el aire que sale tiene que volver a entrar",
                "parrafos": [
                    "Todo el aire que saca la campana tiene que reponerse. Si la cocina no tiene "
                    "por dónde tomarlo, el extractor trabaja contra un recinto en depresión: la "
                    "campana tira menos, las puertas cuestan al abrirse y el humo se queda.",
                    "La inyección de aire de reposición lo resuelve con aire exterior que entra de "
                    "forma controlada, en la cantidad que la extracción necesita. Es el mismo "
                    "principio de los sistemas de ventilación, aplicado a la cocina.",
                ],
                "enlace": {
                    "slug": "ventilacion-inyeccion-de-aire",
                    "texto": "Cómo funcionan la inyección y la extracción de aire",
                },
            },
            {
                "h2": "Por qué una campana industrial no saca el humo",
                "parrafos": [
                    "Cuando la cocina sigue con humo u olor, se revisa en terreno qué parte del "
                    "sistema lo está limitando y se propone la corrección para esa parte. Lo que "
                    "se revisa:",
                ],
                "lista": [
                    "Un extractor que quedó chico para la campana o que perdió rendimiento",
                    "Un ducto muy largo, con demasiadas curvas o con uniones que pierden aire",
                    "Una descarga al exterior obstruida o mal ubicada",
                    "Filtros de la campana saturados de grasa",
                    "Falta de aire de reposición en la cocina",
                ],
            },
            {
                "h2": "Qué conviene tener a mano para cotizar",
                "parrafos": [
                    "Con estos datos la primera conversación avanza más rápido y la visita en "
                    "terreno parte con lo básico resuelto:",
                ],
                "lista": [
                    "Qué equipos de cocción hay (cocina, plancha, freidora, horno) y cuántos",
                    "Las medidas aproximadas de la cocina y la altura del cielo",
                    "Cuántas horas al día funciona y en qué horario se puede trabajar",
                    "Si ya hay una campana o un ducto, y por dónde sale hoy al exterior",
                ],
            },
        ],
        # Ningún proyecto del catálogo es una cocina: se muestran las obras de
        # extracción, y el título lo dice así para no dar a entender otra cosa.
        "etiquetas_proyectos": ["Extracción"],
        "titulo_proyectos": "Otras obras de extracción y ventilación de MAX SERVICES",
        "faq": [
            {
                "p": "¿Qué incluye un sistema de extracción para una cocina industrial?",
                "r": "La campana sobre los equipos de cocción, el ducto y el extractor hasta la "
                     "descarga al exterior y, cuando la cocina lo necesita, la inyección de aire "
                     "de reposición.",
            },
            {
                "p": "¿Por qué la campana de la cocina no saca bien el humo?",
                "r": "Puede ser el extractor, el recorrido del ducto, la descarga, los filtros "
                     "saturados de grasa o la falta de aire de reposición. Se revisa en terreno "
                     "cuál es y se propone la corrección para esa parte.",
            },
            {
                "p": "¿Una cocina industrial necesita inyección de aire?",
                "r": "Si el recinto no tiene por dónde reponer el aire que saca la campana, sí: "
                     "sin reposición el extractor rinde menos y el humo se queda. Se define en la "
                     "evaluación.",
            },
            {
                "p": "¿Trabajan en cocinas que ya están funcionando?",
                "r": "Sí. Se puede mejorar o reemplazar la parte del sistema que lo necesita, "
                     "coordinando los trabajos con el horario de la cocina.",
            },
            {
                "p": "¿La extracción de la cocina entra en la mantención?",
                "r": "Sí. La mantención preventiva y correctiva de MAX SERVICES cubre los sistemas "
                     "de extracción, con un plan según el uso y el estado de la instalación.",
            },
        ],
    },
    {
        "slug": "presurizacion-de-escaleras",
        "numero": "05",
        "nombre": "Presurización de caja de escaleras",
        "nombre_corto": "Presurización",
        "titulo_seo": "Presurización de escaleras en Santiago | Max Services",
        "h1": "Presurización de caja de escaleras para edificios en Santiago",
        "descripcion_seo": (
            "Presurización de escaleras para edificios en Santiago: diseño, montaje y pruebas del "
            "sistema que mantiene el humo fuera de la vía de evacuación."
        ),
        "resumen": "Diseño y montaje de sistemas para seguridad y control de aire en edificios.",
        "tarjeta": "Aplicación en circulaciones protegidas y recintos de apoyo.",
        "servicio_formulario": "presurizacion",
        "imagen": "assets/home/contact-evaluation.webp",
        # La foto muestra a un técnico con una planilla, no un equipo de presurización.
        "imagen_alt": "Técnico de MAX SERVICES registrando la revisión de un equipo en terreno.",
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
                # 03-11-2026: "sala de presurización" 4 impresiones en posicion 6 y
                # "escaleras presurizadas" en la 10 (Search Console); en el
                # autocompletado, "sala de presurización en edificios" y "equipos /
                # ventiladores para presurización de escaleras".
                "h2": "El equipo y la sala de presurización",
                "parrafos": [
                    "El sistema se arma con un ventilador que toma aire del exterior y lo inyecta "
                    "a la caja de escaleras por ductos y rejillas. Ese ventilador se instala en un "
                    "recinto propio, la sala de presurización, o en la ubicación que defina el "
                    "proyecto del edificio, y queda conectado al control que lo activa.",
                    "Una escalera presurizada depende de que ese equipo arranque el día que se "
                    "necesita, por eso el acceso al equipo y su revisión periódica importan tanto "
                    "como el montaje.",
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
                "enlace": {
                    "slug": "mantencion-hvac",
                    "texto": "Mantención de presurización, ventilación y aire acondicionado",
                },
            },
        ],
        "etiquetas_proyectos": ["Presurización"],
        "titulo_proyectos": "Obras con presurización de escaleras",
        "faq": [
            {
                "p": "¿Qué es una escalera presurizada?",
                "r": "Es una caja de escaleras que un sistema mantiene con más presión que los "
                     "pisos, para que el humo de un incendio no entre en la vía de evacuación.",
            },
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
        "numero": "06",
        "nombre": "Mantención preventiva y correctiva",
        "nombre_corto": "Mantención",
        # 03-11-2026: era la peor pagina (posicion 23,8 en 90 dias). Apuntaba a
        # "mantención aire acondicionado santiago", que es una busqueda de casas
        # (Max aparece en la 48-53, contra empresas de hogar con cientos de
        # resenas). El autocompletado tiene la version de empresa: "mantención aire
        # acondicionado empresas", "mantenimiento aire acondicionado oficinas",
        # "mantención extractores de aire", "mantenimiento de presurización de
        # escaleras". Esa es la que esta pagina puede ganar.
        "titulo_seo": "Mantención de aire acondicionado a empresas | Max Services",
        "h1": "Mantención de aire acondicionado y sistemas HVAC para empresas y edificios",
        "descripcion_seo": (
            "Mantención preventiva y correctiva de aire acondicionado, extractores, ventilación "
            "y presurización para empresas, oficinas y edificios en Santiago."
        ),
        "resumen": "Mantención de sistemas HVAC según uso, criticidad y estado de la instalación.",
        "tarjeta": "Revisión programada, ajustes y continuidad de funcionamiento.",
        "servicio_formulario": "mantenciones",
        "imagen": "assets/home/experience-support.webp",
        # La foto muestra ductos y un equipo de cielo, sin personas.
        "imagen_alt": "Ductos de aire y un equipo de climatización de cielo en un recinto técnico.",
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
                "h2": "Mantención de extractores, ventilación y presurización",
                "parrafos": [
                    "La mantención no se limita al aire acondicionado: también cubre los "
                    "extractores, la ventilación y la presurización de escaleras de los edificios, "
                    "que trabajan todo el año y suelen revisarse solo cuando fallan.",
                ],
                "enlace": {
                    "slug": "presurizacion-de-escaleras",
                    "texto": "Cómo funciona la presurización de escaleras",
                },
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
                "p": "¿Hacen mantención de aire acondicionado en oficinas?",
                "r": "Sí. Oficinas y edificios corporativos están entre los recintos que atiende "
                     "la mantención; el plan se ajusta a los horarios en que se puede intervenir "
                     "sin detener el trabajo.",
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
        "numero": "07",
        "nombre": "Reparación de sistemas",
        "nombre_corto": "Reparación",
        "titulo_seo": "Reparación de aire acondicionado en Santiago | Max Services",
        "h1": "Reparación de sistemas de climatización y ventilación en Santiago",
        "descripcion_seo": (
            "Diagnóstico de fallas y reparación de aire acondicionado, ventilación y extracción "
            "para empresas en Santiago, con recomendación escrita de qué conviene."
        ),
        "resumen": "Diagnóstico de fallas, ajustes técnicos y recuperación de operación.",
        "tarjeta": "Apoyo para restablecer continuidad operativa y ejecutar mejoras puntuales.",
        # Sin "servicio_formulario": el formulario no tiene una opcion de reparacion
        # y no se inventa una; la persona elige.
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
