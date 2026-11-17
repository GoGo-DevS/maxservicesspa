/* ===========================================================================
   Navidad 2026: la nieve que cae (version 2, 17-11-2026)
   ===========================================================================

   La franja de saludo, la guirnalda, el gorro y el mono ya vienen en el HTML:
   los decide el servidor por fecha (core/navidad.py) y este archivo solo se
   carga dentro de la ventana. Aqui queda SOLO la nieve que cae.

   La fecha se vuelve a revisar aca por si alguien deja la pagina abierta o
   la sirve una cache vieja: fuera de la ventana no nieva.

   Quien pidio menos movimiento al sistema (prefers-reduced-motion) no ve
   nieve cayendo; lo fijo (franja, guirnalda, gorro) si lo ve. No quitar ese
   respeto: a algunas personas el movimiento les da mareo o migrana.
   =========================================================================== */
(function () {
  "use strict";

  // Hora de Chile: UTC-3 de septiembre a abril (horario de verano).
  var VENTANA = { inicio: "2026-11-16T00:00:00-03:00", fin: "2026-12-26T23:59:59-03:00" };

  var ahora = new Date();
  if (ahora < new Date(VENTANA.inicio) || ahora > new Date(VENTANA.fin)) return;
  if (!document.documentElement.classList.contains("tema-navidad")) return;

  var quieto = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (quieto) return;

  // La portada de Max es clara: un copo blanco solo no se veria. Los copos
  // llevan un borde celeste (el celeste del simbolo de la marca). Se dibujan
  // UNA vez en lienzos chicos y despues solo se copian: dibujar cada copo en
  // cada cuadro le costaria al celular.
  function moldeCristal() {
    var m = document.createElement("canvas");
    m.width = m.height = 64;
    var c = m.getContext("2d");
    if (!c) return m;
    c.translate(32, 32);
    c.lineCap = "round";
    function brazos(color, grosor) {
      c.strokeStyle = color;
      c.lineWidth = grosor;
      for (var i = 0; i < 6; i++) {
        c.save();
        c.rotate(i * Math.PI / 3);
        c.beginPath();
        c.moveTo(0, 0); c.lineTo(0, -26);
        c.moveTo(0, -11); c.lineTo(-7, -17); c.moveTo(0, -11); c.lineTo(7, -17);
        c.moveTo(0, -19); c.lineTo(-5, -24); c.moveTo(0, -19); c.lineTo(5, -24);
        c.stroke();
        c.restore();
      }
    }
    brazos("rgba(70, 150, 205, 0.55)", 7);
    brazos("rgba(255, 255, 255, 1)", 3.4);
    return m;
  }

  function moldePunto() {
    var m = document.createElement("canvas");
    m.width = m.height = 32;
    var c = m.getContext("2d");
    if (!c) return m;
    var g = c.createRadialGradient(16, 16, 0, 16, 16, 16);
    g.addColorStop(0, "rgba(255, 255, 255, 1)");
    g.addColorStop(0.3, "rgba(232, 245, 253, 0.95)");
    g.addColorStop(0.6, "rgba(120, 186, 230, 0.55)");
    g.addColorStop(1, "rgba(120, 186, 230, 0)");
    c.fillStyle = g;
    c.fillRect(0, 0, 32, 32);
    return m;
  }

  function nevar() {
    var lienzo = document.createElement("canvas");
    lienzo.className = "navidad-nieve";
    lienzo.setAttribute("aria-hidden", "true");
    // Fijo, fuera del flujo y sin recibir clics: no mueve nada ni tapa botones.
    // Debajo de la cabecera (z 1020) y del visor de fotos de proyectos (z 1200).
    lienzo.style.cssText = "position:fixed;left:0;top:0;z-index:15;pointer-events:none;";
    document.body.appendChild(lienzo);
    var ctx = lienzo.getContext("2d");
    if (!ctx) return;

    var cristal = moldeCristal();
    var punto = moldePunto();
    var copos = [];
    var ancho = 0, alto = 0, escala = 1, corriendo = false, ultimo = 0;

    function medir() {
      escala = Math.min(window.devicePixelRatio || 1, 2);
      // clientWidth y no innerWidth: innerWidth incluye la barra de scroll.
      ancho = document.documentElement.clientWidth || window.innerWidth;
      alto = window.innerHeight;
      lienzo.width = Math.round(ancho * escala);
      lienzo.height = Math.round(alto * escala);
      lienzo.style.width = ancho + "px";
      lienzo.style.height = alto + "px";
      ctx.setTransform(escala, 0, 0, escala, 0, 0);
      var cuantos = Math.round(Math.min(130, Math.max(34, ancho / 13)));
      while (copos.length < cuantos) copos.push(nuevo(true));
      copos.length = cuantos;
    }

    function nuevo(enCualquierAltura) {
      var esCristal = Math.random() < 0.38;
      var r = esCristal ? 4 + Math.random() * 5.5 : 1.3 + Math.random() * 2.4;
      return {
        cristal: esCristal,
        x: Math.random() * ancho,
        y: enCualquierAltura ? Math.random() * alto : -r * 3,
        r: r,
        v: (esCristal ? 22 : 18) + r * 5 + Math.random() * 14,   // px por segundo
        fase: Math.random() * Math.PI * 2,
        vaiven: 10 + Math.random() * 18,
        giro: Math.random() * Math.PI,
        vgiro: (Math.random() - 0.5) * 0.9,
        a: esCristal ? 0.8 + Math.random() * 0.2 : 0.6 + Math.random() * 0.35
      };
    }

    // Nieve para la llegada: se desvanece al bajar y se detiene del todo
    // cuando ya no se ve, para no gastar bateria mientras alguien lee.
    function opacidad() {
      return Math.max(0, 1 - window.scrollY / (alto * 1.1 || 1));
    }

    function cuadro(t) {
      if (!corriendo) return;
      var dt = Math.min(0.05, ((t - ultimo) / 1000) || 0);
      ultimo = t;
      var op = opacidad();
      lienzo.style.opacity = op.toFixed(3);
      if (op <= 0) { corriendo = false; return; }
      ctx.setTransform(escala, 0, 0, escala, 0, 0);
      ctx.clearRect(0, 0, ancho, alto);
      for (var i = 0; i < copos.length; i++) {
        var c = copos[i];
        c.y += c.v * dt;
        c.fase += dt * 0.9;
        c.giro += c.vgiro * dt;
        if (c.y > alto + c.r * 3) { copos[i] = nuevo(false); continue; }
        var x = c.x + Math.sin(c.fase) * c.vaiven;
        ctx.globalAlpha = c.a;
        if (c.cristal) {
          var d = c.r * 2.6;
          ctx.setTransform(escala, 0, 0, escala, x * escala, c.y * escala);
          ctx.rotate(c.giro);
          ctx.drawImage(cristal, -d / 2, -d / 2, d, d);
          ctx.setTransform(escala, 0, 0, escala, 0, 0);
        } else {
          var p = c.r * 4;
          ctx.drawImage(punto, x - p / 2, c.y - p / 2, p, p);
        }
      }
      ctx.globalAlpha = 1;
      window.requestAnimationFrame(cuadro);
    }

    function arrancar() {
      if (corriendo || document.hidden || opacidad() <= 0) return;
      corriendo = true;
      ultimo = performance.now();
      window.requestAnimationFrame(cuadro);
    }

    medir();
    arrancar();
    window.addEventListener("resize", medir, { passive: true });
    window.addEventListener("scroll", arrancar, { passive: true });
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) corriendo = false; else arrancar();
    });
  }

  if (document.body) nevar();
  else document.addEventListener("DOMContentLoaded", nevar);
})();
