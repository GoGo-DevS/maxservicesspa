# Modulo de Proyectos

Esta base deja la seccion `Proyectos` lista para crecer con carpetas reales de imagenes sin cambiar la interfaz.

## Estructura recomendada

Cada proyecto debe vivir en su propia carpeta:

```text
static/
  assets/
    projects/
      nombre-del-proyecto/
        cover.jpg
        gallery-01.jpg
        gallery-02.jpg
        gallery-03.jpg
```

## Datos que se cargan por proyecto

Cada entrada del archivo [catalog.py](/c:/Users/diego/Desktop/maxservices/portfolio/catalog.py) incluye:

- `slug`
- `name`
- `category`
- `location`
- `summary`
- `description`
- `sector`
- `year`
- `services`
- `asset_dir`
- `cover`
- `gallery`
- `featured`

## Flujo para agregar un proyecto nuevo

1. Crear una carpeta en `static/assets/projects/<slug>/`.
2. Copiar la portada como `cover.jpg`.
3. Copiar la galeria con nombres `gallery-01.jpg`, `gallery-02.jpg`, etc.
4. Agregar una nueva entrada en [catalog.py](/c:/Users/diego/Desktop/maxservices/portfolio/catalog.py).
5. Si el proyecto debe aparecer en la home, dejar `featured: true`.
6. Abrir la ruta `/proyectos/` y validar filtros, card y galeria.

## Categorias disponibles

- `climatizacion`
- `ventilacion`
- `extraccion`
- `presurizacion`
- `mantencion`
- `otros`

## Recomendacion de imagenes

- Portada: 1600x1200 px minimo
- Galeria: mantener misma relacion visual por proyecto
- Formato recomendado: `.jpg` o `.webp`
- Evitar fotos oscuras, pixeladas o con marcas de agua

## Fallback temporal

Si un archivo de imagen aun no existe, el modulo muestra una pieza visual generada automaticamente para que la interfaz siga funcionando mientras cargas material real.
