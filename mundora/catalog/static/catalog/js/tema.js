/* Gestiona el tema y conserva la preferencia del visitante. */
(() => {
    const clave = "mundora-tema";
    const raiz = document.documentElement;
    const preferenciaSistema = window.matchMedia(
        "(prefers-color-scheme: dark)"
    );

    let tema = preferenciaSistema.matches ? "oscuro" : "claro";

    // Recupera la elección previa si el navegador permite almacenarla.
    try {
        const guardado = localStorage.getItem(clave);

        if (guardado === "claro" || guardado === "oscuro") {
            tema = guardado;
        }
    } catch {
        // El cambio de tema funciona aunque el almacenamiento esté bloqueado.
    }

    // Aplica el tema antes de mostrar el contenido.
    raiz.dataset.tema = tema;

    document.addEventListener("DOMContentLoaded", () => {
        const boton = document.getElementById("boton-tema");

        if (!boton) {
            return;
        }

        const actualizarBoton = () => {
            const oscuro = raiz.dataset.tema === "oscuro";

            boton.textContent = oscuro ? "Modo claro" : "Modo oscuro";
            boton.setAttribute(
                "aria-label",
                oscuro ? "Activar modo claro" : "Activar modo oscuro"
            );
        };

        boton.hidden = false;
        actualizarBoton();

        boton.addEventListener("click", () => {
            const nuevoTema = (
                raiz.dataset.tema === "oscuro" ? "claro" : "oscuro"
            );

            raiz.dataset.tema = nuevoTema;

            try {
                localStorage.setItem(clave, nuevoTema);
            } catch {
                // Mantiene el tema elegido durante esta visita.
            }

            actualizarBoton();
        });
    });
})();