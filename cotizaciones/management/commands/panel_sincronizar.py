from django.core.management.base import BaseCommand, CommandError

from cotizaciones import avisos, correo
from cotizaciones.sincronizar import sincronizar


class Command(BaseCommand):
    help = (
        "Lee contacto@ (solo lectura) y arma las solicitudes del panel. "
        "Con --avisar manda el aviso de demoras si corresponde al turno."
    )

    def add_arguments(self, parser):
        parser.add_argument("--dias", type=int, default=None,
                            help="Dias hacia atras en la primera lectura (por defecto 45).")
        parser.add_argument("--maximo", type=int, default=1000)
        parser.add_argument("--avisar", action="store_true",
                            help="Manda el aviso si es hora de aviso (9 y 15 h habiles).")
        parser.add_argument("--avisar-ahora", action="store_true",
                            help="Manda el aviso aunque no sea la hora.")

    def handle(self, *args, **opts):
        try:
            r = sincronizar(dias=opts["dias"], maximo=opts["maximo"])
        except correo.FaltaCredencial as exc:
            raise CommandError(str(exc))
        self.stdout.write(
            "Correo: {leidos} leidos | {nuevas} solicitudes nuevas | {respuestas} respuestas | "
            "{reenvios} reenvios | {adjuntados} agregados a una existente | "
            "{ya_estaban} ya estaban | {omitidos} omitidos | {errores} errores | "
            "{formularios} formularios recuperados".format(**r)
        )
        if opts["avisar"] or opts["avisar_ahora"]:
            res = avisos.enviar_avisos(forzar=opts["avisar_ahora"])
            if res.get("enviado"):
                self.stdout.write(f"Aviso enviado a {', '.join(res['para'])}: {res['cantidad']}.")
            else:
                self.stdout.write(f"Sin aviso: {res.get('motivo')}.")
        if r["errores"]:
            raise CommandError(f"{r['errores']} correos no se pudieron procesar (ver el log).")
