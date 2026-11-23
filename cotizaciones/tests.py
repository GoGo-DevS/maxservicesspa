"""Pruebas del panel de cotizaciones.

Los casos salen del correo real de contacto@ (20-10 al 23-11-2026): reenvios
a fda@ que parecian respuesta, la autorespuesta del formulario, agencias que
escriben "cotizaciones" en el asunto, clientes que vuelven a escribir.
"""
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid
from smtplib import SMTPException
from unittest import mock
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.db import connection
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from core.emailing import _build_contact_context
from core.models import ContactRequest

from . import avisos, correo
from .models import Evento, Mensaje, Sincronizacion, Solicitud
from .permisos import GRUPO_PANEL, GRUPO_RESPONDE
from .sincronizar import procesar_lote, registrar_formulario, sincronizar

CHILE = ZoneInfo("America/Santiago")
# Hash rapido solo en pruebas: el de produccion tarda medio segundo por clave.
HASH_RAPIDO = override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
CLIENTE = "claudia@clinica-ejemplo.cl"


def hora(anio, mes, dia, h=10, m=0):
    return datetime(anio, mes, dia, h, m, tzinfo=CHILE)


def crudo(de, para, asunto, cuerpo, *, cc=None, message_id=None, en_respuesta_a=None,
          reply_to=None, fecha=None, adjunto=None, cabeceras=None):
    msg = EmailMessage()
    msg["From"] = de
    msg["To"] = para
    if cc:
        msg["Cc"] = cc
    if reply_to:
        msg["Reply-To"] = reply_to
    msg["Subject"] = asunto
    msg["Date"] = format_datetime(fecha or hora(2026, 11, 12))
    msg["Message-ID"] = message_id or make_msgid(domain="prueba.cl")
    if en_respuesta_a:
        msg["In-Reply-To"] = en_respuesta_a
        msg["References"] = en_respuesta_a
    for k, v in (cabeceras or {}).items():
        msg[k] = v
    msg.set_content(cuerpo)
    if adjunto:
        msg.add_attachment(b"%PDF-1.4", maintype="application", subtype="pdf", filename=adjunto)
    return msg.as_bytes()


def parseado(*args, uid=1, hilo="", **kw):
    return correo.parsear(crudo(*args, **kw), uid=uid, hilo=hilo)


PEDIDO = (
    "Estimados: Junto con saludar, me comunico con ustedes para solicitar una "
    "cotización por el servicio de mantención de equipos de aire acondicionado "
    "en nuestras instalaciones."
)


class LectorFalso:
    def __init__(self, mensajes, uidvalidity=7):
        self.mensajes = mensajes  # {uid: (bytes, hilo)}
        self._uidvalidity = uidvalidity
        self.carpeta = "[Gmail]/Todos"
        self.pedidos = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def uidvalidity(self):
        return self._uidvalidity

    def uids(self, desde, dias):
        self.pedidos.append(desde)
        return sorted(u for u in self.mensajes if u >= desde)

    def traer(self, uid):
        datos, hilo = self.mensajes[uid]
        return correo.parsear(datos, uid=uid, hilo=hilo)


# ---------------------------------------------------------------- lectura

class ParseoTests(TestCase):
    def test_lee_cabeceras_hilo_y_adjuntos(self):
        m = parseado(
            "Claudia Ramírez <%s>" % CLIENTE, "contacto@maxservicesspa.cl",
            "Solicitud de cotización", PEDIDO,
            cc="otra@clinica-ejemplo.cl", en_respuesta_a="<previo@x>",
            adjunto="planta.pdf", uid=55, hilo="1849",
        )
        self.assertEqual(m["de"], CLIENTE)
        self.assertEqual(m["nombre"], "Claudia Ramírez")
        self.assertEqual(m["para"], ["contacto@maxservicesspa.cl"])
        self.assertEqual(m["cc"], ["otra@clinica-ejemplo.cl"])
        self.assertIn("<previo@x>", m["en_respuesta_a"])
        self.assertEqual(m["adjuntos"], ["planta.pdf"])
        self.assertEqual((m["uid"], m["hilo"]), (55, "1849"))
        self.assertIn("mantención", m["cuerpo"])

    def test_html_sin_texto_plano_se_aplana(self):
        msg = EmailMessage()
        msg["From"] = CLIENTE
        msg["To"] = "contacto@maxservicesspa.cl"
        msg["Subject"] = "Cotización"
        msg.set_content("<p>Hola<br>necesito <b>presupuesto</b></p>", subtype="html")
        m = correo.parsear(msg.as_bytes())
        self.assertIn("necesito presupuesto", m["cuerpo"].replace("\n", " "))
        self.assertTrue(m["message_id"].startswith("<sin-id-"))


class ClasificacionTests(TestCase):
    """Textos reales (resumidos) de contacto@ entre el 27-10 y el 23-11."""

    def test_agencias_que_venden_no_son_cotizacion(self):
        casos = [
            ("Una pregunta sobre sus cotizaciones",
             "¿Cómo están gestionando hoy las solicitudes de cotización que llegan desde su web? "
             "Si prefiere no recibir más correos míos, responda \"baja\" y no le vuelvo a escribir."),
            ("Cotizaciones después de la visita",
             "Ayudamos a pymes a ordenar el seguimiento de sus ventas. Si prefieren no recibir "
             "más mensajes de ATÓMICAS, respondan «no» y no volveré a escribirles."),
            ("PUBLICIDAD: MAX SERVICES SPA: una idea para conectar cotizaciones y seguimiento",
             "Desarrollamos sistemas a medida para conectar cotizaciones."),
            ("Tus trabajos en terreno, ordenados en un solo lugar",
             "Te permite enviar cotizaciones y cobrar. Si no quieres recibir más correos, avísame."),
            ("Selección de licitaciones de climatización",
             "Si prefieren que no vuelva a escribirles sobre esta oferta, basta con responder."),
        ]
        for asunto, cuerpo in casos:
            with self.subTest(asunto=asunto):
                self.assertEqual(correo.clasificar(asunto, cuerpo), "otro")

    def test_pedidos_reales_son_cotizacion(self):
        self.assertEqual(correo.clasificar("Solicitud de cotización", PEDIDO), "cotizacion")
        self.assertEqual(
            correo.clasificar(
                "Solicitud de cotización - 15 equipos split inverter con instalación",
                "Necesitamos cotizar 15 equipos para un recinto institucional en Recoleta.",
            ),
            "cotizacion",
        )

    def test_lo_ambiguo_queda_por_revisar(self):
        self.assertEqual(correo.clasificar("Hola", "¿Podemos conversar?"), "dudoso")

    def test_lista_de_correo_es_otro(self):
        self.assertEqual(correo.clasificar("Cotización", PEDIDO, masivo=True), "otro")


class FormularioParseoTests(TestCase):
    """El aviso del formulario se arma con templates/emails/contact_internal.txt.
    Si alguien cambia esa plantilla, esta prueba avisa que el panel deja de
    entenderla."""

    def test_lee_los_campos_de_la_plantilla_real(self):
        cr = ContactRequest.objects.create(
            full_name="Romina Cabezas", company="Via Club", email="romina@viaclub.cl",
            phone="+56 9 1234 5678", service="mantenciones", location="Providencia",
            message="Chiller Blue Box sin funcionar.\nNecesitamos visita esta semana.",
        )
        texto = render_to_string("emails/contact_internal.txt", _build_contact_context(cr))
        self.assertEqual(correo.campo_formulario(texto, "Nombre"), "Romina Cabezas")
        self.assertEqual(correo.campo_formulario(texto, "Empresa o proyecto"), "Via Club")
        self.assertEqual(correo.campo_formulario(texto, "Telefono"), "+56 9 1234 5678")
        self.assertEqual(correo.campo_formulario(texto, "Servicio requerido"), "Mantenciones")
        self.assertEqual(correo.campo_formulario(texto, "Ubicacion"), "Providencia")
        self.assertIn("Chiller Blue Box", correo.mensaje_formulario(texto))
        self.assertNotIn("Puedes responder", correo.mensaje_formulario(texto))


# ---------------------------------------------------------------- sincronizacion

class ProcesarTests(TestCase):
    def setUp(self):
        self.pedido = parseado(
            "Claudia Ramírez <%s>" % CLIENTE, "contacto@maxservicesspa.cl",
            "Solicitud de cotización", PEDIDO, message_id="<pedido@clinica>",
            fecha=hora(2026, 11, 12, 12, 24), hilo="900",
        )

    def _solo(self):
        self.assertEqual(Solicitud.objects.count(), 1)
        return Solicitud.objects.get()

    def test_correo_de_cliente_abre_una_solicitud(self):
        r = procesar_lote([self.pedido])
        s = self._solo()
        self.assertEqual(r["nuevas"], 1)
        self.assertEqual(s.origen, Solicitud.Origen.CORREO)
        self.assertEqual(s.categoria, Solicitud.Categoria.COTIZACION)
        self.assertEqual(s.estado, Solicitud.Estado.NUEVA)
        self.assertEqual(s.cliente_email, CLIENTE)
        self.assertEqual(s.esperando_desde, hora(2026, 11, 12, 12, 24))
        self.assertEqual(s.gmail_hilo, "900")
        self.assertEqual(s.mensajes.get().sentido, Mensaje.Sentido.ENTRANTE)
        self.assertTrue(s.eventos.filter(tipo=Evento.Tipo.CREADA).exists())

    def test_leer_dos_veces_no_duplica(self):
        procesar_lote([self.pedido])
        r = procesar_lote([dict(self.pedido)])
        self._solo()
        self.assertEqual(Mensaje.objects.count(), 1)
        self.assertEqual(r["ya_estaban"], 1)

    def test_respuesta_desde_contacto_marca_respondida(self):
        respuesta = parseado(
            "contacto@maxservicesspa.cl", CLIENTE, "RE: Solicitud de cotización",
            "Hola Claudia, te proponemos una visita técnica.",
            en_respuesta_a="<pedido@clinica>", fecha=hora(2026, 11, 12, 16), hilo="900",
        )
        r = procesar_lote([self.pedido, respuesta])
        s = self._solo()
        self.assertEqual(r["respuestas"], 1)
        self.assertEqual(s.estado, Solicitud.Estado.RESPONDIDA)
        self.assertIsNone(s.esperando_desde)
        self.assertEqual(s.respondida_por, "contacto@maxservicesspa.cl")

    def test_reenvio_a_fda_no_es_respuesta(self):
        """El patron de octubre: se reenviaba a fda@ y ahi moria."""
        reenvio = parseado(
            "contacto@maxservicesspa.cl", "fda@maxservicesspa.cl",
            "Fwd: Solicitud de cotización", "---------- Forwarded message ---------",
            en_respuesta_a="<pedido@clinica>", fecha=hora(2026, 11, 12, 13), hilo="900",
        )
        r = procesar_lote([self.pedido, reenvio])
        s = self._solo()
        self.assertEqual(r["reenvios"], 1)
        self.assertEqual(r["respuestas"], 0)
        self.assertEqual(s.estado, Solicitud.Estado.NUEVA)
        self.assertIsNotNone(s.esperando_desde)
        self.assertEqual(s.mensajes.last().sentido, Mensaje.Sentido.INTERNO)
        self.assertTrue(s.eventos.filter(tipo=Evento.Tipo.REENVIO).exists())

    def test_autorespuesta_no_es_respuesta(self):
        web = parseado(
            "contacto@maxservicesspa.cl", "contacto@maxservicesspa.cl",
            "Nueva consulta desde la web MAX SERVICES SPA",
            "Nombre: Romina\nCorreo: romina@viaclub.cl\nServicio requerido: Mantenciones\n\n"
            "Mensaje del cliente:\nChiller sin funcionar\n",
            reply_to="romina@viaclub.cl", fecha=hora(2026, 11, 13, 9, 17), uid=1,
        )
        auto = parseado(
            "contacto@maxservicesspa.cl", "romina@viaclub.cl",
            "Hemos recibido tu solicitud | MAX SERVICES SPA", "Gracias por escribirnos.",
            fecha=hora(2026, 11, 13, 9, 17), uid=2,
        )
        procesar_lote([web, auto])
        s = self._solo()
        self.assertEqual(s.origen, Solicitud.Origen.WEB)
        self.assertEqual(s.estado, Solicitud.Estado.NUEVA)
        self.assertIsNone(s.respondida_en)
        self.assertTrue(s.mensajes.filter(automatico=True).exists())

    def test_respuesta_de_fda_con_copia_a_contacto_cuenta(self):
        respuesta = parseado(
            "Felipe Dinamarca <fda@maxservicesspa.cl>", CLIENTE, "RE: Solicitud de cotización",
            "Claudia, adjunto la cotización.", cc="contacto@maxservicesspa.cl",
            en_respuesta_a="<pedido@clinica>", fecha=hora(2026, 11, 13, 10),
        )
        procesar_lote([self.pedido, respuesta])
        s = self._solo()
        self.assertEqual(s.estado, Solicitud.Estado.RESPONDIDA)
        self.assertEqual(s.respondida_por, "fda@maxservicesspa.cl")

    def test_cliente_vuelve_a_escribir_queda_esperando_otra_vez(self):
        respuesta = parseado(
            "contacto@maxservicesspa.cl", CLIENTE, "RE: Solicitud", "Visita el jueves.",
            en_respuesta_a="<pedido@clinica>", fecha=hora(2026, 11, 12, 16),
            message_id="<resp@max>",
        )
        otra = parseado(
            CLIENTE, "contacto@maxservicesspa.cl", "RE: Solicitud", "¿Y el valor?",
            en_respuesta_a="<resp@max>", fecha=hora(2026, 11, 14, 9),
        )
        procesar_lote([self.pedido, respuesta, otra])
        s = self._solo()
        self.assertEqual(s.estado, Solicitud.Estado.RESPONDIDA)  # la etapa no retrocede
        self.assertEqual(s.esperando_desde, hora(2026, 11, 14, 9))
        self.assertTrue(s.eventos.filter(tipo=Evento.Tipo.CLIENTE).exists())

    def test_colega_del_cliente_en_el_mismo_hilo_se_cuelga(self):
        colega = parseado(
            "jefa@clinica-ejemplo.cl", "contacto@maxservicesspa.cl", "RE: Solicitud",
            "Les reitero la solicitud.", en_respuesta_a="<pedido@clinica>",
            fecha=hora(2026, 11, 16, 9),
        )
        procesar_lote([self.pedido, colega])
        s = self._solo()
        self.assertEqual(s.mensajes.count(), 2)

    def test_avisos_de_sistemas_se_ignoran(self):
        ig = parseado(
            "Instagram <no-reply@mail.instagram.com>", "contacto@maxservicesspa.cl",
            "Descubre lo que han compartido", "Ponte al día", fecha=hora(2026, 11, 10),
        )
        r = procesar_lote([ig])
        self.assertEqual(Solicitud.objects.count(), 0)
        self.assertEqual(r["omitidos"], 1)

    def test_agencia_queda_en_otros_y_no_espera(self):
        agencia = parseado(
            "Tomás <ventas@agencia.cl>", "contacto@maxservicesspa.cl",
            "Una pregunta sobre sus cotizaciones",
            "Si prefiere no recibir más correos míos, responda baja.",
        )
        procesar_lote([agencia])
        s = self._solo()
        self.assertEqual(s.categoria, Solicitud.Categoria.OTRO)
        self.assertIsNone(s.esperando_desde)

    def test_un_correo_malo_no_frena_a_los_demas(self):
        malo = {"message_id": "<malo@x>", "de": None}
        r = procesar_lote([malo, self.pedido])
        self.assertEqual(r["errores"], 1)
        self._solo()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_EMAIL="contacto@maxservicesspa.cl",
    DEFAULT_FROM_EMAIL="contacto@maxservicesspa.cl",
)
class FormularioEnPanelTests(TestCase):
    def _post(self):
        return self.client.post(
            "/contacto/",
            {
                "full_name": "Romina Cabezas", "company": "Via Club", "email": "romina@viaclub.cl",
                "phone": "+56 9 1234 5678", "service": "mantenciones",
                "region": "Metropolitana de Santiago", "city": "Santiago", "commune": "Providencia",
                "message": "Chiller Blue Box sin funcionar, necesitamos visita.",
            },
        )

    def _contact_request(self, **kw):
        datos = dict(
            full_name="Romina Cabezas", email="romina@viaclub.cl", service="mantenciones",
            message="Chiller sin funcionar",
        )
        datos.update(kw)
        return ContactRequest.objects.create(**datos)

    def test_registrar_usa_los_message_id_de_los_correos(self):
        cr = self._contact_request()
        s = registrar_formulario(cr, {"aviso": "<aviso@max>", "confirmacion": "<conf@max>"})
        self.assertEqual(s.origen, Solicitud.Origen.WEB)
        self.assertEqual(s.contact_request, cr)
        self.assertTrue(s.mensajes.filter(message_id="<aviso@max>", sentido="entrante").exists())
        self.assertTrue(s.mensajes.filter(message_id="<conf@max>", automatico=True).exists())
        # Al leer el correo despues, el aviso con ese Message-ID no duplica nada.
        aviso = parseado(
            "contacto@maxservicesspa.cl", "contacto@maxservicesspa.cl",
            "Nueva consulta desde la web MAX SERVICES SPA", "Correo: romina@viaclub.cl",
            reply_to="romina@viaclub.cl", message_id="<aviso@max>", fecha=cr.created_at,
        )
        r = procesar_lote([aviso])
        self.assertEqual(r["ya_estaban"], 1)
        self.assertEqual(Solicitud.objects.count(), 1)

    def test_aviso_con_otro_message_id_tampoco_duplica(self):
        cr = self._contact_request()
        registrar_formulario(cr, {})
        aviso = parseado(
            "contacto@maxservicesspa.cl", "contacto@maxservicesspa.cl",
            "Nueva consulta desde la web MAX SERVICES SPA", "Correo: romina@viaclub.cl",
            reply_to="romina@viaclub.cl", fecha=cr.created_at + timedelta(minutes=1),
        )
        procesar_lote([aviso])
        s = Solicitud.objects.get()
        self.assertEqual(s.mensajes.filter(sentido="entrante").count(), 1)

    def test_si_la_base_se_perdio_el_aviso_rearma_la_solicitud(self):
        cuerpo = render_to_string(
            "emails/contact_internal.txt",
            _build_contact_context(self._contact_request(company="Via Club")),
        )
        ContactRequest.objects.all().delete()
        aviso = parseado(
            "contacto@maxservicesspa.cl", "contacto@maxservicesspa.cl",
            "Nueva consulta desde la web MAX SERVICES SPA", cuerpo,
            reply_to="romina@viaclub.cl", fecha=hora(2026, 11, 18, 16, 7),
        )
        procesar_lote([aviso])
        s = Solicitud.objects.get()
        self.assertEqual(s.cliente_empresa, "Via Club")
        self.assertEqual(s.servicio, "Mantenciones")
        self.assertIn("Chiller", s.detalle)

    def test_el_formulario_de_la_web_deja_la_solicitud_en_el_panel(self):
        resp = self._post()
        self.assertEqual(resp.status_code, 302)
        s = Solicitud.objects.get()
        aviso, confirmacion = mail.outbox[0], mail.outbox[1]
        self.assertEqual(s.mensajes.get(sentido="entrante").message_id, aviso.extra_headers["Message-ID"])
        self.assertEqual(
            s.mensajes.get(automatico=True).message_id, confirmacion.extra_headers["Message-ID"]
        )

    def test_si_falla_el_correo_igual_queda_en_el_panel(self):
        with mock.patch("core.views.send_contact_request_notification", side_effect=SMTPException("x")):
            resp = self._post()
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Solicitud.objects.count(), 1)

    def test_si_falla_el_panel_el_formulario_sigue_funcionando(self):
        with mock.patch("cotizaciones.sincronizar.registrar_formulario", side_effect=RuntimeError("x")):
            resp = self._post()
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(ContactRequest.objects.count(), 1)
        self.assertEqual(Solicitud.objects.count(), 0)


class SincronizarTests(TestCase):
    def _lector(self, uidvalidity=7):
        return LectorFalso(
            {
                10: (crudo(CLIENTE, "contacto@maxservicesspa.cl", "Solicitud de cotización", PEDIDO,
                           fecha=hora(2026, 11, 12), message_id="<diez@x>"), "1"),
                11: (crudo("otro@empresa.cl", "contacto@maxservicesspa.cl", "Cotizar extracción",
                           "Necesitamos cotizar extracción.", fecha=hora(2026, 11, 13),
                           message_id="<once@x>"), "2"),
            },
            uidvalidity=uidvalidity,
        )

    def test_lee_y_despues_sigue_desde_el_ultimo_uid(self):
        lector = self._lector()
        r = sincronizar(lector=lector)
        self.assertEqual(r["nuevas"], 2)
        estado = Sincronizacion.actual()
        self.assertEqual((estado.ultimo_uid, estado.uidvalidity), (11, 7))
        lector.mensajes[12] = (crudo("c@d.cl", "contacto@maxservicesspa.cl", "Cotización", PEDIDO), "3")
        sincronizar(lector=lector)
        self.assertEqual(lector.pedidos, [0, 12])
        self.assertEqual(Solicitud.objects.count(), 3)

    def test_si_cambia_uidvalidity_relee_desde_cero_sin_duplicar(self):
        sincronizar(lector=self._lector(7))
        lector = self._lector(8)
        r = sincronizar(lector=lector)
        self.assertEqual(lector.pedidos, [0])
        self.assertEqual(r["ya_estaban"], 2)
        self.assertEqual(Solicitud.objects.count(), 2)

    def test_un_fallo_de_conexion_queda_registrado(self):
        class Roto(LectorFalso):
            def __enter__(self):
                raise OSError("sin red")

        with self.assertRaises(OSError):
            sincronizar(lector=Roto({}))
        self.assertIn("sin red", Sincronizacion.actual().ultimo_error)


# ---------------------------------------------------------------- avisos

def solicitud(**kw):
    datos = dict(
        origen=Solicitud.Origen.CORREO, cliente_email=CLIENTE, asunto="Solicitud",
        recibida_en=hora(2026, 11, 16, 9), esperando_desde=hora(2026, 11, 16, 9),
    )
    datos.update(kw)
    return Solicitud.objects.create(**datos)


class DiasHabilesTests(TestCase):
    def test_salta_el_fin_de_semana(self):
        # viernes 20-11 17:00 -> lunes 23-11 17:00 = un dia habil
        self.assertAlmostEqual(avisos.dias_habiles(hora(2026, 11, 20, 17), hora(2026, 11, 23, 17)), 1.0)
        self.assertAlmostEqual(avisos.dias_habiles(hora(2026, 11, 16, 9), hora(2026, 11, 17, 9)), 1.0)
        self.assertEqual(avisos.dias_habiles(hora(2026, 11, 21, 9), hora(2026, 11, 22, 20)), 0.0)

    def test_hasta_antes_que_desde_es_cero(self):
        self.assertEqual(avisos.dias_habiles(hora(2026, 11, 17), hora(2026, 11, 16)), 0.0)


@override_settings(
    PANEL_AVISO_PARA=["fda@maxservicesspa.cl"], PANEL_AVISO_CC=["diego@ejemplo.cl"],
    PANEL_AVISO_HORAS=[9, 15], SITE_URL="https://maxservicesspa.cl",
)
class AvisosTests(TestCase):
    def setUp(self):
        self.vencida = solicitud(cliente_empresa="GITPRO", esperando_desde=hora(2026, 11, 18, 9))
        solicitud(cliente_empresa="Reciente", esperando_desde=hora(2026, 11, 23, 8))
        solicitud(cliente_empresa="Agencia", categoria=Solicitud.Categoria.OTRO,
                  esperando_desde=hora(2026, 11, 2))
        solicitud(cliente_empresa="Cerrada", estado=Solicitud.Estado.GANADA,
                  esperando_desde=hora(2026, 11, 2))
        self.lunes_9 = hora(2026, 11, 23, 9, 5)

    def test_solo_cotizaciones_abiertas_con_mas_de_un_dia(self):
        self.assertEqual(avisos.vencidas(self.lunes_9), [self.vencida])

    def test_manda_un_correo_por_turno(self):
        res = avisos.enviar_avisos(self.lunes_9)
        self.assertTrue(res["enviado"])
        self.assertEqual(len(mail.outbox), 1)
        enviado = mail.outbox[0]
        self.assertEqual(enviado.to, ["fda@maxservicesspa.cl"])
        self.assertEqual(enviado.cc, ["diego@ejemplo.cl"])
        self.assertIn("GITPRO", enviado.body)
        self.assertIn(f"https://maxservicesspa.cl/panel/{self.vencida.pk}/", enviado.body)
        self.assertNotIn("Reciente", enviado.body)
        self.assertTrue(self.vencida.eventos.filter(tipo=Evento.Tipo.AVISO).exists())
        # Mismo turno: no repite.
        self.assertFalse(avisos.enviar_avisos(self.lunes_9 + timedelta(minutes=30))["enviado"])
        self.assertEqual(len(mail.outbox), 1)
        # Siguiente turno (15:00): vuelve a avisar.
        self.assertTrue(avisos.enviar_avisos(hora(2026, 11, 23, 15, 2))["enviado"])

    def test_fuera_de_hora_o_fin_de_semana_no_avisa(self):
        self.assertFalse(avisos.enviar_avisos(hora(2026, 11, 23, 11))["enviado"])
        self.assertFalse(avisos.enviar_avisos(hora(2026, 11, 21, 9, 5))["enviado"])
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(avisos.enviar_avisos(hora(2026, 11, 23, 11), forzar=True)["enviado"])

    def test_respondida_deja_de_avisar(self):
        self.vencida.marcar_respondida(hora(2026, 11, 20), "contacto@maxservicesspa.cl")
        res = avisos.enviar_avisos(self.lunes_9)
        self.assertFalse(res["enviado"])
        self.assertEqual(res["motivo"], "nada vencido")


# ---------------------------------------------------------------- vistas

@HASH_RAPIDO
@override_settings(PANEL_IMAP_PASSWORD="", PANEL_IMAP_USER="")
class PanelVistasTests(TestCase):
    def setUp(self):
        cache.clear()
        User = get_user_model()
        self.felipe = User.objects.create_user("fda@maxservicesspa.cl", "fda@maxservicesspa.cl",
                                               "clave-larga-felipe", first_name="Felipe")
        self.felipe.groups.add(Group.objects.get(name=GRUPO_RESPONDE))
        self.diego = User.objects.create_user("diego@ejemplo.cl", "diego@ejemplo.cl", "clave-larga-diego")
        self.diego.groups.add(Group.objects.get(name=GRUPO_PANEL))
        self.ajeno = User.objects.create_user("otro@ejemplo.cl", "otro@ejemplo.cl", "clave-larga-otro")
        self.s = solicitud(cliente_empresa="Clínica Ejemplo", esperando_desde=timezone.now())

    def test_sin_sesion_va_a_entrar(self):
        resp = self.client.get("/panel/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp["Location"].startswith("/panel/entrar/?next="))

    def test_cuenta_sin_grupo_no_entra(self):
        self.client.force_login(self.ajeno)
        self.assertEqual(self.client.get("/panel/").status_code, 403)
        self.assertEqual(self.client.get(f"/panel/{self.s.pk}/").status_code, 403)

    def test_bandeja_muestra_la_solicitud_y_no_se_indexa(self):
        self.client.force_login(self.diego)
        resp = self.client.get("/panel/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Clínica Ejemplo")
        self.assertContains(resp, "Sin ver")
        self.assertEqual(resp["X-Robots-Tag"], "noindex, nofollow")
        self.assertContains(resp, '<meta name="robots" content="noindex, nofollow">', html=False)

    def test_felipe_al_abrir_la_marca_vista_diego_no(self):
        self.client.force_login(self.diego)
        self.client.get(f"/panel/{self.s.pk}/")
        self.s.refresh_from_db()
        self.assertIsNone(self.s.vista_en)
        self.assertEqual(self.s.estado, Solicitud.Estado.NUEVA)

        self.client.force_login(self.felipe)
        self.client.get(f"/panel/{self.s.pk}/")
        self.s.refresh_from_db()
        self.assertEqual(self.s.vista_por, self.felipe)
        self.assertEqual(self.s.estado, Solicitud.Estado.VISTA)
        self.assertEqual(self.s.eventos.filter(tipo=Evento.Tipo.VISTA).count(), 1)

        self.client.force_login(self.diego)
        resp = self.client.get("/panel/")
        self.assertContains(resp, "Vista por Felipe")

    def test_cambiar_etapa(self):
        self.client.force_login(self.felipe)
        url = f"/panel/{self.s.pk}/accion/"
        self.client.post(url, {"accion": "estado", "valor": "cotizada"})
        self.s.refresh_from_db()
        self.assertEqual(self.s.estado, Solicitud.Estado.COTIZADA)
        self.assertIsNone(self.s.esperando_desde)
        self.assertTrue(self.s.eventos.filter(tipo=Evento.Tipo.ESTADO).exists())

    def test_etapa_inventada_no_se_guarda(self):
        self.client.force_login(self.felipe)
        self.client.post(f"/panel/{self.s.pk}/accion/", {"accion": "estado", "valor": "pagada"})
        self.s.refresh_from_db()
        self.assertEqual(self.s.estado, Solicitud.Estado.NUEVA)

    def test_marcar_respondida_a_mano(self):
        self.client.force_login(self.felipe)
        self.client.post(f"/panel/{self.s.pk}/accion/", {"accion": "estado", "valor": "respondida"})
        self.s.refresh_from_db()
        self.assertEqual(self.s.estado, Solicitud.Estado.RESPONDIDA)
        self.assertIsNone(self.s.esperando_desde)
        self.assertEqual(self.s.respondida_por, "Felipe")

    def test_no_es_cotizacion_y_vuelta_atras(self):
        self.client.force_login(self.felipe)
        url = f"/panel/{self.s.pk}/accion/"
        self.client.post(url, {"accion": "categoria", "valor": "otro"})
        self.s.refresh_from_db()
        self.assertIsNone(self.s.esperando_desde)
        resp = self.client.get("/panel/")
        self.assertNotContains(resp, "Clínica Ejemplo")
        self.client.post(url, {"accion": "categoria", "valor": "cotizacion"})
        self.s.refresh_from_db()
        self.assertEqual(self.s.esperando_desde, self.s.recibida_en)

    def test_acciones_solo_por_post(self):
        self.client.force_login(self.felipe)
        self.assertEqual(self.client.get(f"/panel/{self.s.pk}/accion/").status_code, 405)

    def test_solicitud_inexistente_es_404(self):
        self.client.force_login(self.felipe)
        self.assertEqual(self.client.get("/panel/999999/").status_code, 404)

    def test_bandeja_no_hace_una_consulta_por_fila(self):
        """G-04: /growth/ de GoGoCRM llego a 60 s por consultas por fila."""
        self.client.force_login(self.diego)
        self.client.get("/panel/")  # calienta sesion y grupos
        with CaptureQueriesContext(connection) as pocas:
            self.client.get("/panel/")
        for i in range(25):
            s = solicitud(cliente_email=f"c{i}@x.cl", esperando_desde=timezone.now(),
                          vista_por=self.felipe, vista_en=timezone.now())
            Mensaje.objects.create(solicitud=s, message_id=f"<m{i}@x>", sentido="entrante",
                                   de=s.cliente_email, fecha=timezone.now())
        with CaptureQueriesContext(connection) as muchas:
            self.client.get("/panel/")
        self.assertEqual(len(pocas), len(muchas))

    def test_sin_clave_de_correo_no_intenta_leer(self):
        self.client.force_login(self.diego)
        with mock.patch("cotizaciones.views.sincronizar") as sinc:
            self.assertEqual(self.client.get("/panel/").status_code, 200)
        sinc.assert_not_called()

    def test_robots_bloquea_el_panel(self):
        self.assertIn("Disallow: /panel/", self.client.get("/robots.txt").content.decode())


@HASH_RAPIDO
class EntrarTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user("fda@maxservicesspa.cl", "fda@maxservicesspa.cl",
                                                         "clave-larga-felipe")
        self.user.groups.add(Group.objects.get(name=GRUPO_RESPONDE))

    def test_entra_y_llega_a_la_bandeja(self):
        resp = self.client.post("/panel/entrar/", {"username": "fda@maxservicesspa.cl",
                                                   "password": "clave-larga-felipe"})
        self.assertRedirects(resp, "/panel/", fetch_redirect_response=False)

    def test_bloquea_despues_de_muchos_intentos(self):
        for _ in range(8):
            self.client.post("/panel/entrar/", {"username": "fda@maxservicesspa.cl", "password": "mala"})
        resp = self.client.post("/panel/entrar/", {"username": "fda@maxservicesspa.cl",
                                                   "password": "clave-larga-felipe"})
        self.assertEqual(resp.status_code, 429)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_pagina_de_entrar_no_se_indexa(self):
        resp = self.client.get("/panel/entrar/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["X-Robots-Tag"], "noindex, nofollow")


@override_settings(PANEL_CRON_TOKEN="token-de-prueba-largo")
class TareaTests(TestCase):
    URL = "/panel/tareas/correo/"

    def test_sin_token_o_con_token_malo_403(self):
        self.assertEqual(self.client.post(self.URL).status_code, 403)
        self.assertEqual(self.client.post(self.URL, HTTP_X_PANEL_TOKEN="otro").status_code, 403)

    @override_settings(PANEL_CRON_TOKEN="")
    def test_sin_token_configurado_queda_apagada(self):
        self.assertEqual(self.client.post(self.URL, HTTP_X_PANEL_TOKEN="").status_code, 403)

    def test_con_token_lee_y_avisa(self):
        with mock.patch("cotizaciones.views.sincronizar", return_value={"nuevas": 2}) as sinc, \
                mock.patch("cotizaciones.views.avisos.enviar_avisos",
                           return_value={"enviado": False, "motivo": "nada vencido"}) as av:
            resp = self.client.post(self.URL, HTTP_X_PANEL_TOKEN="token-de-prueba-largo")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["sincronizacion"], {"nuevas": 2})
        sinc.assert_called_once()
        av.assert_called_once()

    def test_get_no_sirve(self):
        self.assertEqual(self.client.get(self.URL).status_code, 405)


@HASH_RAPIDO
@override_settings(SITE_URL="https://maxservicesspa.cl")
class InvitarTests(TestCase):
    def test_crea_la_cuenta_y_manda_el_enlace(self):
        call_command("panel_invitar", "fda@maxservicesspa.cl", "--nombre", "Felipe", "--responde")
        user = get_user_model().objects.get(username="fda@maxservicesspa.cl")
        self.assertTrue(user.groups.filter(name=GRUPO_RESPONDE).exists())
        self.assertTrue(user.has_usable_password())
        self.assertEqual(len(mail.outbox), 1)
        cuerpo = mail.outbox[0].body
        enlace = next(l for l in cuerpo.split() if "/panel/clave/" in l)
        ruta = enlace.replace("https://maxservicesspa.cl", "")
        resp = self.client.get(ruta, follow=True)
        self.assertContains(resp, "Elige tu clave")
        resp = self.client.post(resp.redirect_chain[-1][0],
                                {"new_password1": "Climatiza-2026!", "new_password2": "Climatiza-2026!"})
        self.assertRedirects(resp, reverse("cotizaciones:clave_lista"), fetch_redirect_response=False)
        user.refresh_from_db()
        self.assertTrue(user.check_password("Climatiza-2026!"))


# ---------------------------------------------------------------- adjuntos

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


def correo_con_adjuntos(message_id="<planos@cliente>"):
    msg = EmailMessage()
    msg["From"] = CLIENTE
    msg["To"] = "contacto@maxservicesspa.cl"
    msg["Subject"] = "Cotización con planos"
    msg["Message-ID"] = message_id
    msg.set_content(PEDIDO)
    msg.add_attachment(PNG, maintype="image", subtype="png", filename="FIRMANEW.png")
    msg.add_attachment(b"%PDF-1.4 planos", maintype="application", subtype="pdf", filename="planta.pdf")
    msg.add_attachment(b"<script>alert(1)</script>", maintype="text", subtype="html", filename="raro.html")
    return msg.as_bytes()


class LectorDeAdjuntos:
    llamadas = 0
    crudo = None

    def __init__(self, *a, **kw):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def buscar_por_message_id(self, message_id):
        LectorDeAdjuntos.llamadas += 1
        return LectorDeAdjuntos.crudo


@HASH_RAPIDO
class AdjuntosTests(TestCase):
    def setUp(self):
        cache.clear()
        LectorDeAdjuntos.llamadas = 0
        LectorDeAdjuntos.crudo = correo_con_adjuntos()
        User = get_user_model()
        self.diego = User.objects.create_user("diego@ejemplo.cl", "diego@ejemplo.cl", "clave-larga-diego")
        self.diego.groups.add(Group.objects.get(name=GRUPO_PANEL))
        self.ajeno = User.objects.create_user("otro@ejemplo.cl", "otro@ejemplo.cl", "clave-larga-otro")
        procesar_lote([correo.parsear(LectorDeAdjuntos.crudo, uid=1)])
        self.msj = Mensaje.objects.get()
        self.lector = mock.patch("cotizaciones.views.correo.LectorImap", LectorDeAdjuntos)
        self.lector.start()
        self.addCleanup(self.lector.stop)

    def url(self, n):
        return reverse("cotizaciones:adjunto", args=[self.msj.pk, n])

    def test_la_sincronizacion_guarda_los_nombres(self):
        self.assertEqual(self.msj.adjuntos, ["FIRMANEW.png", "planta.pdf", "raro.html"])

    def test_la_ficha_muestra_miniatura_de_imagen_y_enlace_al_pdf(self):
        self.client.force_login(self.diego)
        html = self.client.get(f"/panel/{self.msj.solicitud_id}/").content.decode()
        self.assertIn(f'<img src="{self.url(0)}"', html)
        self.assertIn(f'href="{self.url(1)}"', html)
        self.assertNotIn(f'<img src="{self.url(1)}"', html)

    def test_imagen_y_pdf_se_ven_en_el_navegador(self):
        self.client.force_login(self.diego)
        img = self.client.get(self.url(0))
        self.assertEqual(img.status_code, 200)
        self.assertEqual(img["Content-Type"], "image/png")
        self.assertTrue(img["Content-Disposition"].startswith("inline"))
        self.assertEqual(img.content, PNG)
        self.assertIn("sandbox", img["Content-Security-Policy"])
        pdf = self.client.get(self.url(1))
        self.assertEqual(pdf["Content-Type"], "application/pdf")
        self.assertTrue(pdf["Content-Disposition"].startswith("inline"))

    def test_un_html_adjunto_se_descarga_y_nunca_se_abre_como_pagina(self):
        self.client.force_login(self.diego)
        resp = self.client.get(self.url(2))
        self.assertEqual(resp["Content-Type"], "application/octet-stream")
        self.assertTrue(resp["Content-Disposition"].startswith("attachment"))
        self.assertEqual(resp["X-Content-Type-Options"], "nosniff")

    def test_varias_miniaturas_del_mismo_correo_leen_gmail_una_vez(self):
        self.client.force_login(self.diego)
        self.client.get(self.url(0))
        self.client.get(self.url(1))
        self.assertEqual(LectorDeAdjuntos.llamadas, 1)

    def test_solo_el_equipo_ve_los_adjuntos(self):
        resp = self.client.get(self.url(0))
        self.assertEqual(resp.status_code, 302)
        self.client.force_login(self.ajeno)
        self.assertEqual(self.client.get(self.url(0)).status_code, 403)
        self.assertEqual(LectorDeAdjuntos.llamadas, 0)

    def test_indice_inexistente_404(self):
        self.client.force_login(self.diego)
        self.assertEqual(self.client.get(self.url(9)).status_code, 404)

    def test_si_el_correo_ya_no_esta_404_con_aviso(self):
        LectorDeAdjuntos.crudo = None
        self.client.force_login(self.diego)
        resp = self.client.get(self.url(0))
        self.assertEqual(resp.status_code, 404)
        self.assertIn("ya no está", resp.content.decode())

    def test_si_gmail_falla_502_sin_romper(self):
        self.client.force_login(self.diego)
        with mock.patch.object(LectorDeAdjuntos, "buscar_por_message_id", side_effect=OSError("sin red")):
            resp = self.client.get(self.url(0))
        self.assertEqual(resp.status_code, 502)
