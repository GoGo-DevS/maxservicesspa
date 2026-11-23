"""Lectura de contacto@maxservicesspa.cl por IMAP y clasificacion de correos.

Portado de GoGoCRM (core/seguimiento_max.py, 02-11-2026, 16 pruebas). Reglas
que se mantienen:

- Sesion de solo lectura y BODY.PEEK: el panel no marca nada como leido. La
  casilla la usan personas; un flag del correo no puede ser la memoria.
- "Respondido" = un correo que SALE de @maxservicesspa.cl con el cliente en To
  o Cc. Un reenvio a fda@ no es respuesta, aunque Gmail lo muestre en Enviados
  junto al nombre del cliente. La autorespuesta tampoco.
- Lo ambiguo no se bota: queda "Por revisar" y Felipe decide.
"""
from __future__ import annotations

import email
import html
import imaplib
import re
from datetime import date, timedelta, timezone as dt_timezone
from email.header import decode_header, make_header
from email.utils import getaddresses, parsedate_to_datetime

from django.conf import settings

DOMINIO = "maxservicesspa.cl"
TOPE_BYTES = 300_000  # los adjuntos (planos, PDF) quedan fuera del texto
TOPE_EXTRACTO = 4000

ASUNTO_FORMULARIO = "nueva consulta desde la web"
ASUNTO_AUTORESPUESTA = "hemos recibido tu solicitud"

_REMITENTE_SISTEMA = re.compile(
    r"(no-?reply|noresponder|no-responder|mailer-daemon|postmaster|bounce|"
    r"notificaciones?@|notifications?@|dmarc|alert)",
    re.I,
)
_DOMINIO_SISTEMA = {
    "google.com", "googlemail.com", "accounts.google.com", "facebookmail.com",
    "linkedin.com", "render.com", "github.com", "microsoft.com", "mercadopago.cl",
    "mercadolibre.cl", "dev.tiktok.com", "metamail.com", "brevo.com",
    "mail.instagram.com", "instagram.com", "openai.com", "tm.openai.com",
}

_PISTA_CLIENTE = re.compile(
    r"(cotiza|presupuesto|visita t[eé]cnica|solicitud de|requerimiento|"
    r"mantenci[oó]n|reparaci[oó]n|instalaci[oó]n|reubicaci[oó]n|necesitamos|"
    r"necesito|licitaci[oó]n|partidas|propuesta para (nuestro|nuestra|el edificio))",
    re.I,
)
_PISTA_PROVEEDOR = re.compile(
    r"(propuesta comercial|les escribo desde|te escribo desde|"
    r"nuestros servicios|ofrecemos|financiamiento|abogad|empleos|rastreo gps|"
    r"proveedor|distribuidor|cat[aá]logo de productos|suministros industriales|"
    r"fijaciones|soportaci[oó]n|webinar|expo |diario financiero|newsletter|"
    r"revis[eé] su formulario|edici[oó]n especial)",
    re.I,
)
# Lenguaje de envio masivo: quien escribe asi le esta vendiendo algo a Max.
# Pesa mas que cualquier pista de cliente ("Una pregunta sobre sus
# cotizaciones" de una agencia trae la palabra cotizacion).
_MARCA_MASIVO = re.compile(
    r"(recibir m[aá]s (correos|mensajes|emails|comunicaciones)|"
    r"(vuelvo|vuelva|volver[eé]) a escribir|darse de baja|desuscrib|unsubscribe|"
    r"respond(a|an)\s+[«\"']?(baja|no)\b|^publicidad)",
    re.I | re.M,
)


class FaltaCredencial(Exception):
    """No hay clave para leer la casilla."""


# ---------------------------------------------------------------- utilidades

def texto_cabecera(valor) -> str:
    try:
        return str(make_header(decode_header(valor or "")))
    except Exception:
        return valor or ""


def direcciones(valor) -> list[str]:
    return [d.strip().lower() for _, d in getaddresses([valor or ""]) if "@" in d]


def es_propio(direccion: str) -> bool:
    return (direccion or "").lower().endswith("@" + DOMINIO)


def es_sistema(direccion: str) -> bool:
    direccion = (direccion or "").lower()
    dominio = direccion.rsplit("@", 1)[-1]
    return bool(_REMITENTE_SISTEMA.search(direccion)) or dominio in _DOMINIO_SISTEMA


def _html_a_texto(htm: str) -> str:
    htm = re.sub(r"(?is)<(script|style).*?</\1>", " ", htm or "")
    htm = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>|</li>", "\n", htm)
    texto = html.unescape(re.sub(r"<[^>]+>", " ", htm))
    texto = re.sub(r"[ \t\xa0]+", " ", texto)
    return re.sub(r"\n\s*\n+", "\n\n", texto).strip()


def cuerpo_y_adjuntos(msg) -> tuple[str, list[str]]:
    plano, htm, adjuntos = "", "", []
    for parte in msg.walk() if msg.is_multipart() else [msg]:
        nombre = parte.get_filename()
        if nombre:
            adjuntos.append(texto_cabecera(nombre)[:160])
            continue
        tipo = parte.get_content_type()
        if tipo not in ("text/plain", "text/html"):
            continue
        try:
            crudo = parte.get_payload(decode=True) or b""
            txt = crudo.decode(parte.get_content_charset() or "utf-8", "replace")
        except Exception:
            continue
        if tipo == "text/plain" and not plano:
            plano = txt
        elif tipo == "text/html" and not htm:
            htm = txt
    return (plano.strip() or _html_a_texto(htm)), adjuntos


def _fecha(msg):
    try:
        d = parsedate_to_datetime(msg.get("Date"))
    except Exception:
        return None
    if d is None:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt_timezone.utc)
    return d.astimezone(dt_timezone.utc)


def _ids(valor) -> list[str]:
    return re.findall(r"<[^<>\s]+>", valor or "")


def parsear(crudo: bytes, uid=None, hilo="") -> dict:
    """Convierte los bytes de un correo en el dict que usa la sincronizacion."""
    msg = email.message_from_bytes(crudo)
    nombre, de = (getaddresses([msg.get("From") or ""]) or [("", "")])[0]
    cuerpo, adjuntos = cuerpo_y_adjuntos(msg)
    message_id = (msg.get("Message-ID") or "").strip()
    if not message_id:
        # Sin Message-ID no hay como deduplicar; se arma uno estable.
        message_id = f"<sin-id-{uid or 0}-{hilo or 0}@panel.{DOMINIO}>"
    return {
        "uid": uid,
        "hilo": str(hilo or ""),
        "message_id": message_id[:300],
        "en_respuesta_a": _ids(msg.get("In-Reply-To")) + _ids(msg.get("References")),
        "de": (de or "").lower(),
        "nombre": texto_cabecera(nombre) if nombre else "",
        "para": direcciones(msg.get("To")),
        "cc": direcciones(msg.get("Cc")),
        "responder_a": direcciones(msg.get("Reply-To")),
        "asunto": texto_cabecera(msg.get("Subject"))[:300],
        "fecha": _fecha(msg),
        "masivo": bool(msg.get("List-Unsubscribe") or msg.get("List-Id")),
        "cuerpo": cuerpo[:TOPE_EXTRACTO],
        "adjuntos": adjuntos,
    }


# ---------------------------------------------------------------- formulario

def campo_formulario(cuerpo: str, etiqueta: str) -> str:
    """Un campo del aviso del formulario (templates/emails/contact_internal.txt)."""
    m = re.search(r"^\s*%s:\s*(.+?)\s*$" % re.escape(etiqueta), cuerpo, re.M | re.I)
    valor = m.group(1).strip() if m else ""
    return "" if valor in ("-", "—", "No informado", "No indicado", "None") else valor


def mensaje_formulario(cuerpo: str) -> str:
    m = re.search(
        r"Mensaje del cliente:\s*(.+?)(?:\n\s*Puedes responder directamente|\Z)",
        cuerpo,
        re.S | re.I,
    )
    return m.group(1).strip() if m else ""


def cliente_del_formulario(m: dict) -> str:
    for d in m["responder_a"]:
        if not es_propio(d):
            return d
    correo = campo_formulario(m["cuerpo"], "Correo")
    if "@" in correo:
        return correo.lower()
    for d in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", m["cuerpo"]):
        if not es_propio(d):
            return d.lower()
    return ""


# ---------------------------------------------------------------- clasificacion

def clasificar(asunto: str, cuerpo: str, masivo: bool = False) -> str:
    """Devuelve 'cotizacion', 'dudoso' u 'otro'."""
    texto = f"{asunto}\n{(cuerpo or '')[:2500]}"
    if masivo or _MARCA_MASIVO.search(texto):
        return "otro"
    cliente = bool(_PISTA_CLIENTE.search(texto))
    proveedor = bool(_PISTA_PROVEEDOR.search(texto))
    if cliente and not proveedor:
        return "cotizacion"
    if proveedor and not cliente:
        return "otro"
    return "dudoso"


# ---------------------------------------------------------------- IMAP

def config():
    return {
        "host": getattr(settings, "PANEL_IMAP_HOST", "imap.gmail.com"),
        "usuario": getattr(settings, "PANEL_IMAP_USER", "") or "",
        "clave": getattr(settings, "PANEL_IMAP_PASSWORD", "") or "",
    }


def hay_credencial() -> bool:
    cfg = config()
    return bool(cfg["usuario"] and cfg["clave"])


def _carpeta_todos(M) -> str:
    """'Todos' trae entrada y salida juntas. Gmail la marca con \\All y el nombre
    cambia con el idioma ([Gmail]/Todos, [Gmail]/All Mail)."""
    try:
        ok, filas = M.list()
    except Exception:
        ok, filas = "NO", []
    if ok == "OK":
        for fila in filas or []:
            texto = fila.decode("utf-8", "replace") if isinstance(fila, bytes) else str(fila)
            if "\\All" in texto:
                m = re.search(r'"([^"]+)"\s*$', texto) or re.search(r"(\S+)\s*$", texto)
                if m:
                    return m.group(1)
    return "INBOX"


_RE_HILO = re.compile(rb"X-GM-THRID (\d+)")
_RE_UID = re.compile(rb"UID (\d+)")


class LectorImap:
    """Lee la casilla en solo lectura. Uso:

        with LectorImap() as lector:
            mensajes, uidvalidity, ultimo = lector.leer(desde_uid, dias)
    """

    def __init__(self, cfg=None, timeout=20):
        self.cfg = cfg or config()
        self.timeout = timeout
        self.M = None
        self.carpeta = ""

    def __enter__(self):
        if not (self.cfg["usuario"] and self.cfg["clave"]):
            raise FaltaCredencial(
                "Falta la clave de contacto@ para leer el correo "
                "(PANEL_IMAP_PASSWORD o EMAIL_HOST_PASSWORD)."
            )
        self.M = imaplib.IMAP4_SSL(self.cfg["host"], 993, timeout=self.timeout)
        self.M.login(self.cfg["usuario"], self.cfg["clave"])
        self.carpeta = _carpeta_todos(self.M)
        nombre = self.carpeta if self.carpeta == "INBOX" else '"%s"' % self.carpeta
        ok, _ = self.M.select(nombre, readonly=True)
        if ok != "OK":
            raise RuntimeError(f"No se pudo abrir la carpeta {self.carpeta}.")
        return self

    def __exit__(self, *exc):
        try:
            self.M.logout()
        except Exception:
            pass

    def uidvalidity(self):
        try:
            ok, datos = self.M.response("UIDVALIDITY")
            return int(datos[0]) if datos and datos[0] else None
        except Exception:
            return None

    def uids(self, desde_uid: int, dias: int) -> list[int]:
        if desde_uid:
            ok, datos = self.M.uid("SEARCH", None, "UID", f"{desde_uid}:*")
        else:
            desde = (date.today() - timedelta(days=dias)).strftime("%d-%b-%Y")
            ok, datos = self.M.uid("SEARCH", None, "SINCE", desde)
        if ok != "OK":
            raise RuntimeError("La casilla no respondió a la búsqueda.")
        uids = sorted(int(u) for u in (datos[0] or b"").split())
        # "UID n:*" siempre devuelve al menos el ultimo, aunque sea menor que n.
        return [u for u in uids if u >= desde_uid]

    def traer(self, uid: int):
        ok, datos = self.M.uid(
            "FETCH", str(uid), "(X-GM-THRID BODY.PEEK[]<0.%d>)" % TOPE_BYTES
        )
        if ok != "OK" or not datos:
            return None
        for parte in datos:
            if isinstance(parte, tuple) and len(parte) == 2:
                cabecera, crudo = parte
                hilo = _RE_HILO.search(cabecera or b"")
                return parsear(crudo, uid=uid, hilo=hilo.group(1).decode() if hilo else "")
        return None
