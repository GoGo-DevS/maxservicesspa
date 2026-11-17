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

   LIVIANA (17-11-2026, Diego la sentia lenta al hacer scroll). Se ve igual,
   pero cuesta mucho menos:
   - el canvas va a 1x (antes devicePixelRatio hasta 2: en un celular retina
     eran 4 veces los pixeles). La nieve es borrosa: no se nota;
   - hasta 90 copos (antes 130);
   - 30 cuadros por segundo (antes 60): se ve igual de fluida;
   - quieta MIENTRAS se hace scroll: no se redibuja hasta 160 ms despues del
     ultimo evento de scroll. Ahi es donde se notaba la lentitud;
   - la barra del navegador del celular (aparece y se esconde al hacer scroll
     y dispara resize) ya no vuelve a crear el canvas;
   - arranca 1,2 s despues de la carga, sin competir con el primer pintado.
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

    // Los moldes de los copos son chicos y siguen en alta; el canvas grande va
    // a 1x (un pixel del canvas por pixel CSS).
    var cristal = moldeCristal();
    var punto = moldePunto();
    var copos = [];
    var ancho = 0, alto = 0, corriendo = false, ultimo = 0, acumulado = 0;
    var quietoHasta = 0, opacidadPuesta = "", pedido = 0;
    var CUADRO = 0.028;      // ~30 cuadros por segundo: en una pantalla de 60 Hz, uno si y uno no
    var PAUSA_SCROLL = 160;  // ms sin redibujar despues del ultimo evento de scroll

    function medir() {
      // clientWidth y no innerWidth: innerWidth incluye la barra de scroll.
      var nuevoAncho = document.documentElement.clientWidth || window.innerWidth;
      var nuevoAlto = window.innerHeight;
      // En el celular la barra del navegador aparece y se esconde al hacer
      // scroll y dispara resize. Si el ancho es el mismo y el alto nuevo cabe
      // en el canvas que ya existe, no se toca: reasignar lienzo.width borra
      // el canvas y pide memoria nueva en pleno scroll. Solo se agranda si el
      // alto crece.
      if (nuevoAncho === ancho && nuevoAlto <= alto) return;
      ancho = nuevoAncho;
      alto = nuevoAlto;
      lienzo.width = ancho;
      lienzo.height = alto;
      lienzo.style.width = ancho + "px";
      lienzo.style.height = alto + "px";
      // 1920 -> 90 copos, 1366 -> 76, 390 -> 28.
      var cuantos = Math.round(Math.min(90, Math.max(28, ancho / 18)));
      while (copos.length < cuantos) copos.push(nuevo(true));
      copos.length = cuantos;
      // Cambiar el tamano borra el canvas: se repinta altiro donde estaba cada
      // copo, para que la nieve no desaparezca si esto pasa en pleno scroll.
      pintar(0);
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
      return Math.max(0, 1 - window.scrollY / (window.innerHeight * 1.1 || 1));
    }

    // La opacidad depende del scroll: se pone en el evento de scroll, no en
    // cada cuadro, y solo si cambio.
    function ponerOpacidad(op) {
      var texto = op.toFixed(3);
      if (texto !== opacidadPuesta) {
        lienzo.style.opacity = texto;
        opacidadPuesta = texto;
      }
    }

    // Un solo ciclo de cuadros a la vez: si se detuvo (corriendo = false) y se
    // vuelve a arrancar antes de que llegue el cuadro pendiente, ese cuadro
    // sigue el ciclo en vez de abrir otro en paralelo.
    function seguir() { pedido = window.requestAnimationFrame(cuadro); }

    function cuadro(t) {
      pedido = 0;
      if (!corriendo) return;
      var paso = Math.max(0, (t - ultimo) / 1000) || 0;
      ultimo = t;
      // Mientras se hace scroll la nieve queda quieta: no se redibuja.
      if (t < quietoHasta) { acumulado = 0; seguir(); return; }
      // 30 cuadros por segundo: se junta el tiempo y se dibuja cada ~33 ms.
      acumulado += paso;
      if (acumulado < CUADRO) { seguir(); return; }
      var dt = Math.min(0.05, acumulado);
      acumulado = 0;
      pintar(dt);
      seguir();
    }

    // Mueve los copos dt segundos y los dibuja (con dt = 0 solo los repinta).
    function pintar(dt) {
      ctx.setTransform(1, 0, 0, 1, 0, 0);
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
          ctx.setTransform(1, 0, 0, 1, x, c.y);
          ctx.rotate(c.giro);
          ctx.drawImage(cristal, -d / 2, -d / 2, d, d);
          ctx.setTransform(1, 0, 0, 1, 0, 0);
        } else {
          var p = c.r * 4;
          ctx.drawImage(punto, x - p / 2, c.y - p / 2, p, p);
        }
      }
      ctx.globalAlpha = 1;
    }

    function arrancar() {
      if (corriendo || document.hidden || opacidad() <= 0) return;
      corriendo = true;
      ultimo = performance.now();
      acumulado = CUADRO;  // el primer cuadro se dibuja altiro
      if (!pedido) seguir();
    }

    // Cada evento de scroll deja la nieve quieta 160 ms mas, actualiza la
    // opacidad y la detiene si ya no se ve (o la vuelve a arrancar al subir).
    function alHacerScroll() {
      quietoHasta = performance.now() + PAUSA_SCROLL;
      var op = opacidad();
      ponerOpacidad(op);
      if (op <= 0) corriendo = false;
      else arrancar();
    }

    medir();
    ponerOpacidad(opacidad());
    arrancar();
    window.addEventListener("resize", medir, { passive: true });
    window.addEventListener("scroll", alHacerScroll, { passive: true });
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) corriendo = false; else arrancar();
    });
  }

  // Arranca 1,2 s despues de la carga (y cuando el navegador esta libre), para
  // no competir con el primer pintado ni con la imagen principal (LCP).
  function despuesDeCargar() {
    window.setTimeout(function () {
      if (window.requestIdleCallback) window.requestIdleCallback(nevar, { timeout: 1000 });
      else nevar();
    }, 1200);
  }

  if (document.readyState === "complete") despuesDeCargar();
  else window.addEventListener("load", despuesDeCargar);
})();
