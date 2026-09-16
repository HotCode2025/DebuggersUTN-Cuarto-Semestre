// -------------------------------------------------------------------------------------------------
// Clase Avatar
class Avatar {
    constructor(nombre, foto, vidas = 3) {
        this.nombre = nombre;
        this.foto = foto;
        this.vidas = vidas;
    }
}

// -------------------------------------------------------------------------------------------------
// Instanciar primeros personajes
let zuko = new Avatar('Zuko', './assets/Zuko.png', 3);
let katara = new Avatar('Katara', './assets/Katara.png', 3);
let aang = new Avatar('Aang', './assets/Aang.png', 3);
let toph = new Avatar('Toph', './assets/Toph.png', 3);

// -------------------------------------------------------------------------------------------------
// Arreglo para almacenar todas las instancias
let avatares = [];
avatares.push(zuko, katara, aang, toph);

// -------------------------------------------------------------------------------------------------
// Estado y variables del juegop
let ataqueJugador;
let ataqueEnemigo;
let vidasJugador = 3;
let vidasEnemigo = 3;
let personajeJugador = null; 
let personajeEnemigo = null; 

// -------------------------------------------------------------------------------------------------
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

// -------------------------------------------------------------------------------------------------
// Botones de reinicio
const botonCambiarPersonaje = document.getElementById('boton-cambiar-personaje');
const botonReiniciar = document.getElementById('boton-reiniciar');

// -------------------------------------------------------------------------------------------------
// Reglas
const popupReglas = document.getElementById('popup-reglas');
const botonReglas = document.getElementById('boton-reglas');
const botonCerrarReglas = document.getElementById('boton-cerrar-reglas');

// -------------------------------------------------------------------------------------------------
// Juego
function iniciarJuego() {
    // Registros de eventos
    botonPersonajeJugador.addEventListener('click', seleccionarPersonajeJugador);
    botonPunio.addEventListener('click', ataquePunio);
    botonPatada.addEventListener('click', ataquePatada);
    botonBarrida.addEventListener('click', ataqueBarrida);
    
    // Eventos de reinicio
    botonCambiarPersonaje.addEventListener('click', reiniciarCombate);
    botonReiniciar.addEventListener('click', reiniciarJuego);

    botonReglas.addEventListener('click', () => popupReglas.showModal());
    botonCerrarReglas.addEventListener('click', () => popupReglas.close());
}

// -------------------------------------------------------------------------------------------------
// Seleccionar personaje
function seleccionarPersonajeJugador() {
    let opcionesPersonajes = document.getElementsByName('personaje');
    let idSeleccionado = "";

    for (let i = 0; i < opcionesPersonajes.length; i++) {
        if (opcionesPersonajes[i].checked) {
            idSeleccionado = opcionesPersonajes[i].id;
            break; 
        }
    }

    personajeJugador = avatares.find(avatar => avatar.nombre.toLowerCase() === idSeleccionado.toLowerCase());

    if (personajeJugador) {
        spanPersonajeJugador.innerHTML = personajeJugador.nombre.toUpperCase();
        vidasJugador = personajeJugador.vidas;
        spanVidasJugador.innerHTML = vidasJugador;
        
        agregarLogConsola(`Jugador seleccionó: ${personajeJugador.nombre.toUpperCase()}`);
        seleccionarPersonajeEnemigo(personajeJugador);
    } else {
        alert('POR FAVOR, SELECCIONA UN PERSONAJE ANTES DE CONTINUAR.');
    }
}

// -------------------------------------------------------------------------------------------------
// Personaje enemigo
function seleccionarPersonajeEnemigo(pJugador) {
    let opcionesEnemigos = avatares.filter(avatar => avatar !== pJugador);
    
    let indiceAleatorio = aleatorio(0, opcionesEnemigos.length - 1);
    personajeEnemigo = opcionesEnemigos[indiceAleatorio];

    spanPersonajeEnemigo.innerHTML = personajeEnemigo.nombre.toUpperCase();
    vidasEnemigo = personajeEnemigo.vidas;
    spanVidasEnemigo.innerHTML = vidasEnemigo;
    
    agregarLogConsola(`Enemigo seleccionó: ${personajeEnemigo.nombre.toUpperCase()}`);
}

// -------------------------------------------------------------------------------------------------
// Ataques
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

// -------------------------------------------------------------------------------------------------
// Combate
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

    agregarLogConsola(`${ataqueJugador} vs ${ataqueEnemigo} | ${resultadoRound}`);
    revisarVidas();
}

// -------------------------------------------------------------------------------------------------
// Vidas
function revisarVidas() {
    if (vidasJugador === 0) {
        finalizarJuego("El enemigo te ha derrotado... 😢");
    } else if (vidasEnemigo === 0) {
        finalizarJuego("¡Felicidades! Has ganado 🏆");
    }
}

// -------------------------------------------------------------------------------------------------
// Finalizar
function finalizarJuego(mensajeFinal) {
    sectionMensajes.innerHTML = `<p style="font-size: 1.2em; color: red;"><strong>${mensajeFinal}</strong></p>`;
    agregarLogConsola(`FIN: ${mensajeFinal}`);

    botonPunio.disabled = true;
    botonPatada.disabled = true;
    botonBarrida.disabled = true;
}

// -------------------------------------------------------------------------------------------------
// Restablece solo el combate para seleccionar otro personaje sin recargar la página
function reiniciarCombate() {
    vidasJugador = 3;
    vidasEnemigo = 3;
    personajeJugador = null;
    personajeEnemigo = null;

    spanPersonajeJugador.innerHTML = '';
    spanPersonajeEnemigo.innerHTML = '';
    spanVidasJugador.innerHTML = '3';
    spanVidasEnemigo.innerHTML = '3';
    sectionMensajes.innerHTML = '<p>¡Selecciona un nuevo personaje para iniciar la batalla!</p>';

    // Habilitar de nuevo los botones de ataque
    botonPunio.disabled = false;
    botonPatada.disabled = false;
    botonBarrida.disabled = false;

    // Desmarcar selecciones previas de radio buttons
    let opcionesPersonajes = document.getElementsByName('personaje');
    opcionesPersonajes.forEach(opcion => opcion.checked = false);

    agregarLogConsola('Reinicio parcial: Selecciona un nuevo personaje.');
}

// -------------------------------------------------------------------------------------------------
// Reinicia por completo el juego
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

function agregarLogConsola(texto) {
    if (consolaLog) {
        let nuevoParrafo = document.createElement('p');
        nuevoParrafo.textContent = `> ${texto}`;
        consolaLog.appendChild(nuevoParrafo);
        consolaLog.scrollTop = consolaLog.scrollHeight;
    }
}

// -------------------------------------------------------------------------------------------------
// -------------------------------------------------------------------------------------------------
window.addEventListener('load', iniciarJuego);