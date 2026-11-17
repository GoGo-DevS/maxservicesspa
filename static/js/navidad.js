/* ===========================================================================
   Navidad 2026: decoracion que se enciende y se apaga SOLA
   ===========================================================================

   Regalo de la mantencion (16-11-2026). Es solo adorno: no dice precios, no
   ofrece nada y no agrega texto. Mismo mecanismo que gogodevs.cl (campana.js).

   Todo nace OCULTO: el CSS solo aplica con html.tema-navidad, y esa clase la
   pone este script unicamente dentro de la ventana.

       sin JS            -> no se ve nada
       antes del 16-11   -> no se ve nada
       dentro            -> luces bajo la cabecera, gorro en el logo y nieve
       despues del 26-12 -> no se ve nada, sin que nadie toque un archivo

   Quien pidio menos movimiento al sistema (prefers-reduced-motion) ve las
   luces quietas y el gorro, pero NO la nieve. No quitar ese respeto.

   PARA SACARLA ANTES: borrar el <script> de templates/base.html.
   PARA EL PROXIMO ANO: cambiar las dos fechas de VENTANA.
   =========================================================================== */
(function () {
  "use strict";

  // Hora de Chile: UTC-3 de septiembre a abril (horario de verano).
  var VENTANA = { inicio: "2026-11-16T00:00:00-03:00", fin: "2026-12-26T23:59:59-03:00" };

  var ahora = new Date();
  if (ahora < new Date(VENTANA.inicio) || ahora > new Date(VENTANA.fin)) return;

  document.documentElement.classList.add("tema-navidad");

  var quieto = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (quieto) return;

  function nevar() {
    var lienzo = document.createElement("canvas");
    lienzo.className = "navidad-nieve";
    lienzo.setAttribute("aria-hidden", "true");
    // Fijo, fuera del flujo y sin recibir clics: no mueve nada ni tapa botones.
    // Debajo de la cabecera (z 1020), del menu del celular y del visor de fotos
    // de proyectos (z 1200).
    lienzo.style.cssText = "position:fixed;left:0;top:0;z-index:15;pointer-events:none;";
    document.body.appendChild(lienzo);
    var ctx = lienzo.getContext("2d");
    if (!ctx) return;

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
      // Pocos copos: es un adorno, no una tormenta que tape el texto.
      var cuantos = Math.round(Math.min(60, Math.max(22, ancho / 22)));
      while (copos.length < cuantos) copos.push(nuevo(true));
      copos.length = cuantos;
    }

    function nuevo(enCualquierAltura) {
      var r = 1 + Math.random() * 2.3;
      return {
        x: Math.random() * ancho,
        y: enCualquierAltura ? Math.random() * alto : -8,
        r: r,
        v: 16 + r * 12 + Math.random() * 10,     // px por segundo
        fase: Math.random() * Math.PI * 2,
        vaiven: 8 + Math.random() * 16,
        a: 0.55 + Math.random() * 0.4
      };
    }

    // La portada de Max es clara: un copo blanco no se veria (y uno blanco con
    // borde parecia una burbuja). Cada copo es un punto celeste palido con el
    // centro blanco y el borde difuso, del celeste del simbolo de la marca.
    // Se dibuja UNA vez en un lienzo chico y despues solo se copia: un
    // degradado por copo y por cuadro le costaria al celular.
    var molde = document.createElement("canvas");
    molde.width = molde.height = 32;
    var mctx = molde.getContext("2d");
    if (mctx) {
      var g = mctx.createRadialGradient(16, 16, 0, 16, 16, 16);
      g.addColorStop(0, "rgba(255, 255, 255, 1)");
      g.addColorStop(0.2, "rgba(214, 236, 250, 0.95)");
      g.addColorStop(0.55, "rgba(140, 196, 234, 0.6)");
      g.addColorStop(1, "rgba(140, 196, 234, 0)");
      mctx.fillStyle = g;
      mctx.fillRect(0, 0, 32, 32);
    }

    function pintarCopo(x, y, c) {
      var d = c.r * 4;
      ctx.globalAlpha = c.a;
      ctx.drawImage(molde, x - d / 2, y - d / 2, d, d);
    }

    // Nieve solo para la llegada: se desvanece al bajar y se detiene del todo
    // cuando ya no se ve, para no gastar bateria mientras alguien lee.
    function opacidad() {
      return Math.max(0, 1 - window.scrollY / (alto * 0.9 || 1));
    }

    function cuadro(t) {
      if (!corriendo) return;
      var dt = Math.min(0.05, ((t - ultimo) / 1000) || 0);
      ultimo = t;
      var op = opacidad();
      lienzo.style.opacity = op.toFixed(3);
      if (op <= 0) { corriendo = false; ctx.clearRect(0, 0, ancho, alto); return; }
      ctx.clearRect(0, 0, ancho, alto);
      for (var i = 0; i < copos.length; i++) {
        var c = copos[i];
        c.y += c.v * dt;
        c.fase += dt * 0.9;
        if (c.y > alto + 8) { copos[i] = nuevo(false); continue; }
        pintarCopo(c.x + Math.sin(c.fase) * c.vaiven, c.y, c);
      }
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
