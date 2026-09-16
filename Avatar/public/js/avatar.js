// -------------------------------------------------------------------------------------------------
// Clase Avatar

class Avatar {
    constructor(nombre, foto = './assets/default.png', vidas = 3) {
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
// Banco de sílabas para nombres aleatorios
const silabasInicio = ['Kor', 'Sok', 'Ir', 'Az', 'Ap', 'Ror', 'Kyo', 'Mak', 'Ten', 'Za', 'Bum', 'Pak', 'Zhao', 'Yue', 'Pian'];
const silabasFin = ['ra', 'ka', 'oh', 'la', 'pa', 'ku', 'shi', 'ko', 'zin', 'heer', 'mi', 'lee', 'dao', 'tan'];

// -------------------------------------------------------------------------------------------------
// Estados y variables del juego
let ataqueJugador;
let ataqueEnemigo;
let vidasJugador = 3;
let vidasEnemigo = 3;
let personajeJugador = null; 
let personajeEnemigo = null; 

// -------------------------------------------------------------------------------------------------
// Nodos del DOM
const contenedorTarjetas = document.getElementById('contenedor-tarjetas');
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
// Ventana Emergente de Reglas
const popupReglas = document.getElementById('popup-reglas');
const botonReglas = document.getElementById('boton-reglas');
const botonCerrarReglas = document.getElementById('boton-cerrar-reglas');

// -------------------------------------------------------------------------------------------------
// Ventana Emergente de Generación Masiva
const popupGenerar = document.getElementById('popup-generar');
const botonAbrirGenerar = document.getElementById('boton-abrir-generar');
const botonGenerarMultiples = document.getElementById('boton-generar-multiples');
const botonCerrarGenerar = document.getElementById('boton-cerrar-generar');
const inputCantidad = document.getElementById('input-cantidad');

// -------------------------------------------------------------------------------------------------
// Inicio del juego
function iniciarJuego() {
    // Renderizar avatares iniciales
    renderizarPersonajes();

    // Eventos principales del juego
    botonPersonajeJugador.addEventListener('click', seleccionarPersonajeJugador);
    botonPunio.addEventListener('click', ataquePunio);
    botonPatada.addEventListener('click', ataquePatada);
    botonBarrida.addEventListener('click', ataqueBarrida);
    
    // Eventos de reinicio
    botonCambiarPersonaje.addEventListener('click', reiniciarCombate);
    botonReiniciar.addEventListener('click', reiniciarJuego);

    // Eventos de Popups
    botonReglas.addEventListener('click', () => popupReglas.showModal());
    botonCerrarReglas.addEventListener('click', () => popupReglas.close());

    botonAbrirGenerar.addEventListener('click', () => popupGenerar.showModal());
    botonCerrarGenerar.addEventListener('click', () => popupGenerar.close());
    botonGenerarMultiples.addEventListener('click', generarMultiplesPersonajes);
}

// Renderiza todas las instancias en el HTML
function renderizarPersonajes() {
    contenedorTarjetas.innerHTML = '';
    avatares.forEach((avatar) => {
        let opcionAvatar = `
            <input type="radio" name="personaje" id="${avatar.nombre.toLowerCase()}" />
            <label for="${avatar.nombre.toLowerCase()}">${avatar.nombre}</label>
        `;
        contenedorTarjetas.innerHTML += opcionAvatar;
    });
}

// -------------------------------------------------------------------------------------------------
// Generar N nuevos personajes
function generarNombreAleatorio() {
    let inicio = silabasInicio[aleatorio(0, silabasInicio.length - 1)];
    let fin = silabasFin[aleatorio(0, silabasFin.length - 1)];
    let sufijo = aleatorio(1, 99);
    return `${inicio}${fin}_${sufijo}`;
}

function generarMultiplesPersonajes() {
    let cantidad = parseInt(inputCantidad.value);

    if (isNaN(cantidad) || cantidad < 1) {
        alert('Ingresa una cantidad válida mayor a 0.');
        return;
    }

    for (let i = 0; i < cantidad; i++) {
        let nombreAleatorio = generarNombreAleatorio();
        let nuevoAvatar = new Avatar(nombreAleatorio);
        avatares.push(nuevoAvatar);
    }

    renderizarPersonajes();
    agregarLogConsola(`Se generaron ${cantidad} personajes aleatorios.`);
    popupGenerar.close();
}

// -------------------------------------------------------------------------------------------------

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

function revisarVidas() {
    if (vidasJugador === 0) {
        finalizarJuego("El enemigo te ha derrotado... 😢");
    } else if (vidasEnemigo === 0) {
        finalizarJuego("¡Felicidades! Has ganado 🏆");
    }
}

function finalizarJuego(mensajeFinal) {
    sectionMensajes.innerHTML = `<p style="font-size: 1.2em; color: red;"><strong>${mensajeFinal}</strong></p>`;
    agregarLogConsola(`FIN: ${mensajeFinal}`);

    botonPunio.disabled = true;
    botonPatada.disabled = true;
    botonBarrida.disabled = true;
}

// -------------------------------------------------------------------------------------------------
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

    botonPunio.disabled = false;
    botonPatada.disabled = false;
    botonBarrida.disabled = false;

    let opcionesPersonajes = document.getElementsByName('personaje');
    opcionesPersonajes.forEach(opcion => opcion.checked = false);

    agregarLogConsola('Reinicio parcial: Selecciona un nuevo personaje.');
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

// -------------------------------------------------------------------------------------------------
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

