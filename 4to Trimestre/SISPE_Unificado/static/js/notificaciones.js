(function () {
  const notificaciones = document.querySelectorAll(".avisos .aviso, .messagelist li");

  notificaciones.forEach(function (notificacion) {
    if (notificacion.dataset.notificacionActiva) return;
    notificacion.dataset.notificacionActiva = "true";
    if (!notificacion.hasAttribute("aria-live")) {
      notificacion.setAttribute("aria-live", "polite");
    }

    const cerrar = document.createElement("button");
    cerrar.type = "button";
    cerrar.className = "notificacion-cerrar";
    cerrar.setAttribute("aria-label", "Cerrar notificación");
    cerrar.textContent = "×";

    function ocultar() {
      notificacion.classList.add("notificacion-saliendo");
      window.setTimeout(function () {
        notificacion.remove();
      }, 250);
    }

    cerrar.addEventListener("click", ocultar);
    notificacion.appendChild(cerrar);
    window.setTimeout(ocultar, notificacion.classList.contains("error") ? 10000 : 6500);
  });
})();
