# Panel de cotizaciones (`/panel/`)

Creado el 23-11-2026. Junta en una bandeja las consultas del formulario web y
los correos que llegan a contacto@maxservicesspa.cl. Registra quién abrió cada
solicitud, cuándo se respondió y en qué etapa va. Dos veces al día hábil avisa
a Felipe de lo que lleva más de un día hábil sin respuesta.

## Cómo decide cada cosa

| Hecho | Regla |
|---|---|
| Solicitud nueva | Correo de alguien de afuera que no calza con una solicitud abierta (mismo hilo o mismo remitente en los últimos 30 días), o un formulario web. |
| Respondida | Sale un correo desde @maxservicesspa.cl **con el cliente en Para o Cc**. Si Felipe responde desde fda@, tiene que poner contacto@ en copia. |
| No es respuesta | Reenvío a fda@ (queda como "Reenvío interno") y la autorespuesta "Hemos recibido tu solicitud". |
| Vista | La abre alguien del grupo **Responde cotizaciones**. Si la abre alguien del grupo **Panel cotizaciones**, no cambia nada. |
| Por revisar | El texto es ambiguo. Felipe decide con "Cotización" o "No es cotización". |
| No es cotización | Agencias, proveedores y avisos masivos (detecta "no recibir más correos", "responda baja", "PUBLICIDAD", listas de correo). |
| Aviso | Cotizaciones abiertas con el cliente esperando 1 día hábil o más (lunes a viernes). Un solo correo a las 9 y a las 15. |

El correo es la fuente de verdad. Si la base se pierde, una sincronización
rearma las solicitudes y vuelve a detectar las respuestas. Lo que se pierde es
lo marcado a mano: etapas, notas y cuentas.

## Puesta en marcha (una vez)

1. **Base persistente.** El sitio usa SQLite y Render borra el archivo en cada
   deploy si el servicio no tiene disco. En Render, en el servicio
   `maxservicesspa`, ir a Disks y agregar un disco de 1 GB montado en
   `/var/data` (unos USD 0,25 al mes). Después:
   - Variable `SQLITE_PATH=/var/data/db.sqlite3`
   - Start Command: `bash start.sh` (migra y arranca gunicorn)
2. **Correo.** El panel lee contacto@ con la misma clave de aplicación del SMTP
   (`EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD`). Si esa clave no sirve para
   IMAP, crear una propia en la cuenta de Google de contacto@ y ponerla en
   `PANEL_IMAP_PASSWORD`.
3. **Avisos.** `PANEL_AVISO_PARA` (por defecto `fda@maxservicesspa.cl`) y
   `PANEL_AVISO_CC` (opcional; correos separados por coma).
4. **Cron.** Generar un token con
   `python -c "import secrets; print(secrets.token_urlsafe(32))"` y ponerlo en
   dos lugares: la variable `PANEL_CRON_TOKEN` en Render y el secret
   `PANEL_CRON_TOKEN` del repo en GitHub. Sin el token, el workflow no hace nada.
5. **Primera lectura.** En la Shell de Render:
   `python manage.py panel_sincronizar` (lee los últimos 45 días).
6. **Cuentas.** En la Shell de Render:
   - `python manage.py panel_invitar fda@maxservicesspa.cl --nombre Felipe --responde`
   - `python manage.py panel_invitar <tu correo> --nombre Diego`

   A cada uno le llega un enlace para elegir su clave. Nadie más la ve.

## Variables

| Variable | Por defecto | Para qué |
|---|---|---|
| `SQLITE_PATH` | `db.sqlite3` del proyecto | Base en un disco persistente |
| `PANEL_IMAP_USER` / `PANEL_IMAP_PASSWORD` | las del SMTP | Leer contacto@ |
| `PANEL_CRON_TOKEN` | vacío (apagado) | Proteger `/panel/tareas/correo/` |
| `PANEL_AVISO_PARA` | `fda@maxservicesspa.cl` | Quién recibe el aviso |
| `PANEL_AVISO_CC` | vacío | Copia del aviso |
| `PANEL_AVISO_HORAS` | `9,15` | Horas de aviso (Chile) |
| `PANEL_AVISO_DIAS_HABILES` | `1` | Desde cuántos días hábiles se avisa |
| `PANEL_DIAS_INICIALES` | `45` | Días hacia atrás en la primera lectura |
| `PANEL_SINCRONIZAR_AL_ABRIR` | `1` | Leer el correo al abrir la bandeja (cada 5 min como máximo) |

## Pendiente (siguiente etapa)

- Responder desde el panel con plantillas por escenario y la identidad de Max
  (necesita los ejemplos de Felipe).
- Cotización en PDF con correlativo, neto, IVA y condiciones (la lógica existe
  en MaxCRM).
- Radar de licitaciones de Mercado Público (existe en MaxCRM:
  `scan_licitaciones_mp`).
