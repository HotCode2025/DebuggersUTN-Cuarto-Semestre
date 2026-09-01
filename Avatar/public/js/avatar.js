// Estado de la partida
let ataqueJugador;
let ataqueEnemigo;
let vidasJugador = 3;
let vidasEnemigo = 3;
let personajeJugador = "";
let personajeEnemigo = "";

// Nodos del DOM
const spanPersonajeJugador = document.getElementById('personaje-jugador');
const spanPersonajeEnemigo = document.getElementById('personaje-enemigo');
const spanVidasJugador = document.getElementById('vidas-jugador');
const spanVidasEnemigo = document.getElementById('vidas-enemigo');
const sectionMensajes = document.getElementById('mensajes');
const consolaLog = document.getElementById('consola-log');

const botonPersonajeJugador = document.getElementById('boton-personaje');
const botonPunio = document.getElementById('boton-punio');
const botonPatada = document.getElementById('boton-patada');
const botonBarrida = document.getElementById('boton-barrida');
const botonReiniciar = document.getElementById('boton-reiniciar');

const popupReglas = document.getElementById('popup-reglas');
const botonReglas = document.getElementById('boton-reglas');
const botonCerrarReglas = document.getElementById('boton-cerrar-reglas');

function iniciarJuego() {
    // Registros de eventos
    botonPersonajeJugador.addEventListener('click', seleccionarPersonajeJugador);
    botonPunio.addEventListener('click', ataquePunio);
    botonPatada.addEventListener('click', ataquePatada);
    botonBarrida.addEventListener('click', ataqueBarrida);
    botonReiniciar.addEventListener('click', reiniciarJuego);

    botonReglas.addEventListener('click', () => popupReglas.showModal());
    botonCerrarReglas.addEventListener('click', () => popupReglas.close());
}

function seleccionarPersonajeJugador() {
    personajeJugador = "";
    let opcionesPersonajes = document.getElementsByName('personaje');

    for (let i = 0; i < opcionesPersonajes.length; i++) {
        if (opcionesPersonajes[i].checked) {
            personajeJugador = opcionesPersonajes[i].id;
            break; 
        }
    }

    if (personajeJugador !== "") {
        spanPersonajeJugador.innerHTML = personajeJugador.toUpperCase();
        
        // Log en consola
        agregarLogConsola(`Jugador seleccionó: ${personajeJugador.toUpperCase()}`);
        
        seleccionarPersonajeEnemigo(personajeJugador);
    } else {
        alert('POR FAVOR, SELECCIONA UN PERSONAJE ANTES DE CONTINUAR.');
    }
}

function seleccionarPersonajeEnemigo(pJugador) {
    personajeEnemigo = "";

    do {
        let numeroAleatorio = aleatorio(1, 4);

        if (numeroAleatorio === 1) personajeEnemigo = "zuko";
        else if (numeroAleatorio === 2) personajeEnemigo = "katara";
        else if (numeroAleatorio === 3) personajeEnemigo = "aang";
        else if (numeroAleatorio === 4) personajeEnemigo = "toph";
    } while (personajeEnemigo === pJugador);

    spanPersonajeEnemigo.innerHTML = personajeEnemigo.toUpperCase();
    
    // Log en consola
    agregarLogConsola(`Enemigo seleccionó: ${personajeEnemigo.toUpperCase()}`);
}

// Handlers de ataque
function ataquePunio() {
    ataqueJugador = 'Puño';
    funcionCombate();
}

function ataquePatada() {
    ataqueJugador = 'Patada';
    funcionCombate();
}

function ataqueBarrida() {
    ataqueJugador = 'Barrida';
    funcionCombate();
}

function funcionCombate() {
    if (!personajeJugador) {
        alert('Primero debes seleccionar un personaje.');
        return;
    }

    ataqueAleatorioEnemigo();
    combate();
}

function combate() {
    let resultadoRound = "";

    if (ataqueJugador === ataqueEnemigo) {
        resultadoRound = "EMPATE 🤝";
    } 
    else if ((ataqueJugador === 'Patada' && ataqueEnemigo === 'Puño') ||
        (ataqueJugador === 'Puño' && ataqueEnemigo === 'Barrida') ||
        (ataqueJugador === 'Barrida' && ataqueEnemigo === 'Patada')) {
            resultadoRound = "GANASTE EL ROUND 🎉";
            vidasEnemigo--;
            spanVidasEnemigo.innerHTML = vidasEnemigo; 
    } 
    else {
        resultadoRound = "PERDISTE EL ROUND ❌";
        vidasJugador--;
        spanVidasJugador.innerHTML = vidasJugador; 
    }

    sectionMensajes.innerHTML = `<p>Tu personaje atacó con <strong>${ataqueJugador}</strong>, el enemigo atacó con <strong>${ataqueEnemigo}</strong> - <strong>${resultadoRound}</strong></p>`;

    // Registrar acción en la ventana de debug
    agregarLogConsola(`${ataqueJugador} vs ${ataqueEnemigo} | ${resultadoRound}`);

    revisarVidas();
}

function revisarVidas() {
    if (vidasJugador === 0) {
        finalizarJuego("El enemigo te ha derrotado... 😢");
    } else if (vidasEnemigo === 0) {
        finalizarJuego("¡Felicidades! Has ganado 🏆");
    }
}

function finalizarJuego(mensajeFinal) {
    sectionMensajes.innerHTML = `<p style="font-size: 1.2em; color: red;"><strong>${mensajeFinal}</strong></p>`;

    // Log de fin de juego
    agregarLogConsola(`FIN: ${mensajeFinal}`);

    botonPunio.disabled = true;
    botonPatada.disabled = true;
    botonBarrida.disabled = true;
}

function reiniciarJuego() {
    location.reload();
}

function ataqueAleatorioEnemigo() {
    let ataqueAleatorio = aleatorio(1, 3);

    if (ataqueAleatorio == 1) ataqueEnemigo = 'Puño';
    else if (ataqueAleatorio == 2) ataqueEnemigo = 'Patada';
    else ataqueEnemigo = 'Barrida';
}

function aleatorio(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min);
}

// Imprime un nuevo mensaje en la consola lateral y desplaza el scroll
function agregarLogConsola(texto) {
    if (consolaLog) {
        let nuevoParrafo = document.createElement('p');
        nuevoParrafo.textContent = `> ${texto}`;
        consolaLog.appendChild(nuevoParrafo);
        consolaLog.scrollTop = consolaLog.scrollHeight;
    }
}

window.addEventListener('load', iniciarJuego);