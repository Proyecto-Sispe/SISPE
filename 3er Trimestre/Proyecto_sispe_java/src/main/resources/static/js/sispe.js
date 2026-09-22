/*
 * Comportamiento común de SISPE (retroalimentación al usuario):
 *  - <form data-confirm="¿Seguro?">  pide confirmación antes de enviar (acciones destructivas).
 *  - Los botones de envío se bloquean mientras se procesa, para evitar envíos dobles.
 *  - Los avisos de éxito (.alertas .alert-success) se ocultan solos a los 6 segundos.
 */
(function () {
    'use strict';

    document.addEventListener('submit', function (evento) {
        var formulario = evento.target;
        if (!formulario || !formulario.getAttribute) return;

        var mensaje = formulario.getAttribute('data-confirm');
        if (mensaje && !window.confirm(mensaje)) {
            evento.preventDefault();
            return;
        }

        var boton = formulario.querySelector('button[type="submit"], button:not([type])');
        if (boton && !formulario.hasAttribute('data-no-lock')) {
            // Se difiere un ciclo para que el navegador alcance a enviar el formulario antes de bloquear el botón.
            setTimeout(function () {
                boton.setAttribute('data-texto-original', boton.textContent);
                boton.disabled = true;
                boton.textContent = 'Procesando…';
            }, 0);
        }
    });

    // Si el usuario vuelve con «Atrás», los botones no deben quedar bloqueados.
    window.addEventListener('pageshow', function (evento) {
        if (!evento.persisted) return;
        document.querySelectorAll('button[data-texto-original]').forEach(function (boton) {
            boton.disabled = false;
            boton.textContent = boton.getAttribute('data-texto-original');
        });
    });

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.alertas .alert-success').forEach(function (aviso) {
            setTimeout(function () {
                aviso.classList.add('alerta-oculta');
                setTimeout(function () { aviso.remove(); }, 500);
            }, 6000);
        });
    });
})();
