// ----------------------------------------------------------------------------------------------------------
// Definimos las constantes que usaremos en el juego 
const sectionSeleccionarMascota = document.getElementById('seleccionar-mascota')
const sectionBotonReiniciar = document.getElementById('reiniciar')
const botonMascotaJugador = document.getElementById('boton-mascota')

const botonGenerarPersonajes = document.getElementById('boton-generar-personajes')
const botonConfirmarGenerar = document.getElementById('boton-confirmar-generar')
const modalGenerar = document.getElementById('modal-generar')
const cerrarGenerar = document.getElementById('cerrar-generar')
const inputCantidad = document.getElementById('input-cantidad')

const botonReglasInicio = document.getElementById('boton-reglas-inicio')
const botonReglasMapa = document.getElementById('boton-reglas-mapa')
const modalReglas = document.getElementById('modal-reglas')
const cerrarReglas = document.getElementById('cerrar-reglas')
const botonReiniciar = document.getElementById('boton-reiniciar')

const sectionVerMapa = document.getElementById('ver-mapa')
const mapa = document.getElementById('mapa')

const spanMascotaJugador = document.getElementById('mascota-jugador')
const spanMascotaEnemigo = document.getElementById('mascota-enemigo')
const spanVidasJugador = document.getElementById('vidas-jugador')
const spanVidasEnemigo = document.getElementById('vidas-enemigo')
const estadoCombate = document.getElementById('estado-combate')
const textoResultado = document.getElementById('resultado')

const contenedorTarjetas = document.getElementById('contenedorTarjetas')
const contenedorAtaques = document.getElementById('contenedorAtaques')

// ----------------------------------------------------------------------------------------------------------
// Variables de Juego
let Avatares = []
let enemigosEnMapa = [] 
let enemigosDerrotados = [] // Registro para colocar calaveras
let mascotaJugador
let mascotaJugadorObjeto
let enemigoActual = null

let enCombate = false

let ataqueJugador
let ataqueEnemigo
let vidasJugador = 20
let vidasEnemigo = 3

// Objeto del Baúl del Tesoro
let baul = {
    x: 0,
    y: 0,
    ancho: 60,
    alto: 60,
    abierto: false,
    fotoCerrado: new Image(),
    fotoAbierto: new Image()
}
baul.fotoCerrado.src = './assets/baul_cerrado.png'
baul.fotoAbierto.src = './assets/baul_abierto.png'

// ----------------------------------------------------------------------------------------------------------
// Canvas y Niebla de Guerra
let lienzo = mapa.getContext("2d")
let intervalo
let mapaBackground = new Image()
mapaBackground.src = './assets/mapa.jpg'

const COLUMNAS_MAPA = 3
const FILAS_MAPA = 4
let celdasReveladas = []

// ----------------------------------------------------------------------------------------------------------
// Silabas para armar los nombres de los personajes
const silabasInicio = ['Kor', 'Sok', 'Ir', 'Az', 'Ap', 'Ror', 'Kyo', 'Mak', 'Ten', 'Za', 'Bum', 'Pak', 'Zhao', 'Yue', 'Pian']
const silabasFin = ['ra', 'ka', 'oh', 'la', 'pa', 'ku', 'shi', 'ko', 'zin', 'heer', 'mi', 'lee', 'dao', 'tan']

// ----------------------------------------------------------------------------------------------------------
// Ataques
const ataquesDisponibles = [
    { nombre: '💨 Aire', id: 'boton-aire' },
    { nombre: '🔥 Fuego', id: 'boton-fuego' },
    { nombre: '🌱 Tierra', id: 'boton-tierra' },
    { nombre: '💧 Agua', id: 'boton-agua' }
]

// ----------------------------------------------------------------------------------------------------------
// Clase Avatar
class Avatar {
    constructor(nombre, foto = './assets/aang.webp', vida = 3) {
        this.nombre = nombre
        this.foto = foto
        this.vida = vida
        this.ataques = [...ataquesDisponibles]
        this.x = 20
        this.y = 20
        this.ancho = 60
        this.alto = 60
        this.mapaFoto = new Image()
        this.mapaFoto.src = foto
        this.velocidadX = 0
        this.velocidadY = 0
    }
}

// ----------------------------------------------------------------------------------------------------------
// Imagenes de los Avatar
let aang = new Avatar('Aang', './assets/aang.webp', 3)
let katara = new Avatar('Katara', './assets/katara.webp', 3)
let sokka = new Avatar('Sokka', './assets/sokka.webp', 3)
let haru = new Avatar('Haru', './assets/haru.webp', 3)

Avatares.push(aang, katara, sokka, haru)

// ----------------------------------------------------------------------------------------------------------
// Generador de nuevos personajes
function aleatorio(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min)
}

function generarNombreAleatorio() {
    let inicio = silabasInicio[aleatorio(0, silabasInicio.length - 1)]
    let fin = silabasFin[aleatorio(0, silabasFin.length - 1)]
    let sufijo = aleatorio(1, 99)
    return `${inicio}${fin}_${sufijo}`
}

function generarPersonajes() {
    let cantidad = parseInt(inputCantidad.value)

    if (isNaN(cantidad) || cantidad < 1) {
        alert('Ingresa una cantidad válida mayor a 0.')
        return
    }

    const fotosBase = ['./assets/aang.webp', './assets/katara.webp', './assets/sokka.webp', './assets/haru.webp']

    for (let i = 0; i < cantidad; i++) {
        let nombreAleatorio = generarNombreAleatorio()
        let fotoAleatoria = fotosBase[aleatorio(0, fotosBase.length - 1)]
        let nuevoAvatar = new Avatar(nombreAleatorio, fotoAleatoria)
        Avatares.push(nuevoAvatar)
    }

    renderizarTarjetasPersonajes()
    modalGenerar.style.display = 'none'
}

// ----------------------------------------------------------------------------------------------------------
// Mostrar las tarjetas de los personajes
function renderizarTarjetasPersonajes() {
    contenedorTarjetas.innerHTML = ''
    Avatares.forEach((Avatar, index) => {
        let idUnico = `${Avatar.nombre}_${index}`
        let tarjeta = `
        <input type="radio" name="mascota" id="${idUnico}" value="${Avatar.nombre}" />
        <label class="tarjeta-de-Avatar" for="${idUnico}">
            <p>${Avatar.nombre}</p>
            <img src="${Avatar.foto}" alt="${Avatar.nombre}">
        </label>
        `
        contenedorTarjetas.innerHTML += tarjeta
    })
}

// ----------------------------------------------------------------------------------------------------------
// Mapa y niebla
function inicializarNiebla() {
    celdasReveladas = []
    for (let f = 0; f < FILAS_MAPA; f++) {
        let fila = []
        for (let c = 0; c < COLUMNAS_MAPA; c++) {
            fila.push(false)
        }
        celdasReveladas.push(fila)
    }
}

function revelarTodoElMapa() {
    for (let f = 0; f < FILAS_MAPA; f++) {
        for (let c = 0; c < COLUMNAS_MAPA; c++) {
            celdasReveladas[f][c] = true
        }
    }
}

function UbicarElementosAleatorios() {
    enemigosEnMapa = Avatares.filter(m => m.nombre !== mascotaJugador)
    
    let anchoCelda = mapa.width / COLUMNAS_MAPA
    let altoCelda = mapa.height / FILAS_MAPA

    let celdasDisponibles = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    celdasDisponibles.sort(() => Math.random() - 0.5)

    // Ubicar los primeros 3 enemigos aleatorios
    enemigosEnMapa.forEach((enemigo, idx) => {
        if (idx < 3) {
            let numCelda = celdasDisponibles[idx]
            let col = numCelda % COLUMNAS_MAPA
            let fila = Math.floor(numCelda / COLUMNAS_MAPA)

            enemigo.x = col * anchoCelda + (anchoCelda - enemigo.ancho) / 2
            enemigo.y = fila * altoCelda + (altoCelda - enemigo.alto) / 2
        }
    })
    
    enemigosEnMapa = enemigosEnMapa.slice(0, 3)

    // Ubicar el Baúl en una celda libre restante
    let celdaBaul = celdasDisponibles[3]
    let colBaul = celdaBaul % COLUMNAS_MAPA
    let filaBaul = Math.floor(celdaBaul / COLUMNAS_MAPA)

    baul.x = colBaul * anchoCelda + (anchoCelda - baul.ancho) / 2
    baul.y = filaBaul * altoCelda + (altoCelda - baul.alto) / 2
    baul.abierto = false
}

function iniciarMapa() {
    mapa.width = 640
    mapa.height = 480

    inicializarNiebla()
    UbicarElementosAleatorios()

    intervalo = setInterval(pintarCanvas, 50)

    window.addEventListener('keydown', sePresionoUnaTecla)
    window.addEventListener('keyup', detenerMovimiento)
}

// ----------------------------------------------------------------------------------------------------------
function pintarCanvas() {
    if (!enCombate) {
        mascotaJugadorObjeto.x += mascotaJugadorObjeto.velocidadX
        mascotaJugadorObjeto.y += mascotaJugadorObjeto.velocidadY
    }

    if (mascotaJugadorObjeto.x < 0) mascotaJugadorObjeto.x = 0
    if (mascotaJugadorObjeto.x > mapa.width - mascotaJugadorObjeto.ancho) mascotaJugadorObjeto.x = mapa.width - mascotaJugadorObjeto.ancho
    if (mascotaJugadorObjeto.y < 0) mascotaJugadorObjeto.y = 0
    if (mascotaJugadorObjeto.y > mapa.height - mascotaJugadorObjeto.alto) mascotaJugadorObjeto.y = mapa.height - mascotaJugadorObjeto.alto

    let centroX = mascotaJugadorObjeto.x + mascotaJugadorObjeto.ancho / 2
    let centroY = mascotaJugadorObjeto.y + mascotaJugadorObjeto.alto / 2
    let anchoCelda = mapa.width / COLUMNAS_MAPA
    let altoCelda = mapa.height / FILAS_MAPA

    let colActual = Math.floor(centroX / anchoCelda)
    let filaActual = Math.floor(centroY / altoCelda)

    if (colActual >= 0 && colActual < COLUMNAS_MAPA && filaActual >= 0 && filaActual < FILAS_MAPA) {
        celdasReveladas[filaActual][colActual] = true
    }

    lienzo.clearRect(0, 0, mapa.width, mapa.height)
    lienzo.drawImage(mapaBackground, 0, 0, mapa.width, mapa.height)

    // Dibujar el Baúl (cerrado u abierto)
    let imgBaul = baul.abierto ? baul.fotoAbierto : baul.fotoCerrado
    lienzo.drawImage(imgBaul, baul.x, baul.y, baul.ancho, baul.alto)

    // Dibujar calaveras en las posiciones donde fueron derrotados los enemigos
    enemigosDerrotados.forEach(pos => {
        lienzo.font = "40px Arial"
        lienzo.fillText("💀", pos.x + 10, pos.y + 45)
    })

    // Dibujar enemigos activos
    enemigosEnMapa.forEach(enemigo => {
        lienzo.drawImage(enemigo.mapaFoto, enemigo.x, enemigo.y, enemigo.ancho, enemigo.alto)
        if (!enCombate) {
            revisarColision(enemigo)
        }
    })

    // Dibujar jugador
    lienzo.drawImage(
        mascotaJugadorObjeto.mapaFoto,
        mascotaJugadorObjeto.x,
        mascotaJugadorObjeto.y,
        mascotaJugadorObjeto.ancho,
        mascotaJugadorObjeto.alto
    )

    // Revisar interacción con el baúl si el jugador se aproxima
    if (!enCombate) {
        revisarColisionBaul()
    }

    dibujarNiebla(anchoCelda, altoCelda)
}

// ----------------------------------------------------------------------------------------------------------
function dibujarNiebla(anchoCelda, altoCelda) {
    for (let f = 0; f < FILAS_MAPA; f++) {
        for (let c = 0; c < COLUMNAS_MAPA; c++) {
            if (!celdasReveladas[f][c]) {
                lienzo.fillStyle = "black"
                lienzo.fillRect(c * anchoCelda, f * altoCelda, anchoCelda, altoCelda)
            }
        }
    }
}

// ----------------------------------------------------------------------------------------------------------
function revisarColision(enemigo) {
    const arribaEnemigo = enemigo.y
    const abajoEnemigo = enemigo.y + enemigo.alto
    const derechaEnemigo = enemigo.x + enemigo.ancho
    const izquierdaEnemigo = enemigo.x

    const arribaJugador = mascotaJugadorObjeto.y
    const abajoJugador = mascotaJugadorObjeto.y + mascotaJugadorObjeto.alto
    const derechaJugador = mascotaJugadorObjeto.x + mascotaJugadorObjeto.ancho
    const izquierdaJugador = mascotaJugadorObjeto.x

    if (
        abajoJugador < arribaEnemigo ||
        arribaJugador > abajoEnemigo ||
        derechaJugador < izquierdaEnemigo ||
        izquierdaJugador > derechaEnemigo
    ) {
        return
    }

    detenerMovimiento()
    iniciarCombate(enemigo)
}

// ----------------------------------------------------------------------------------------------------------
// Revisar la interacción del jugador con el baúl
function revisarColisionBaul() {
    const arribaBaul = baul.y
    const abajoBaul = baul.y + baul.alto
    const derechaBaul = baul.x + baul.ancho
    const izquierdaBaul = baul.x

    const arribaJugador = mascotaJugadorObjeto.y
    const abajoJugador = mascotaJugadorObjeto.y + mascotaJugadorObjeto.alto
    const derechaJugador = mascotaJugadorObjeto.x + mascotaJugadorObjeto.ancho
    const izquierdaJugador = mascotaJugadorObjeto.x

    if (
        abajoJugador < arribaBaul ||
        arribaJugador > abajoBaul ||
        derechaJugador < izquierdaBaul ||
        izquierdaJugador > derechaBaul
    ) {
        return
    }

    if (enemigosEnMapa.length > 0) {
        estadoCombate.innerHTML = "🔒 Debes derrotar a todos los personajes para obtener el tesoro."
    } else {
        baul.abierto = true
        estadoCombate.innerHTML = "🎁 ¡Has abierto el Baúl del Tesoro y obtenido tu recompensa final!"
    }
}

// ----------------------------------------------------------------------------------------------------------
// Combate
function iniciarCombate(enemigo) {
    enCombate = true
    enemigoActual = enemigo
    vidasJugador = 20
    vidasEnemigo = 3
    spanVidasJugador.innerHTML = vidasJugador
    spanVidasEnemigo.innerHTML = vidasEnemigo

    spanMascotaEnemigo.innerHTML = enemigo.nombre
    estadoCombate.innerHTML = "⚔️ ¡Combate en curso contra " + enemigo.nombre + "!"
    textoResultado.innerHTML = "Elige tu ataque para pelear"

    mostrarAtaques(mascotaJugadorObjeto.ataques)
}

function mostrarAtaques(ataques) {
    contenedorAtaques.innerHTML = ''
    ataques.forEach((ataque) => {
        let boton = document.createElement('button')
        boton.className = 'boton-de-ataque'
        boton.innerText = ataque.nombre
        boton.onclick = () => seleccionarAtaqueJugador(ataque.nombre)
        contenedorAtaques.appendChild(boton)
    })
}

function seleccionarAtaqueJugador(ataque) {
    if (!enCombate || vidasJugador === 0 || vidasEnemigo === 0) return

    ataqueJugador = ataque
    seleccionarAtaqueAleatorioEnemigo()
    combate()
}

function seleccionarAtaqueAleatorioEnemigo() {
    let ataqueAleatorio = Math.floor(Math.random() * enemigoActual.ataques.length)
    ataqueEnemigo = enemigoActual.ataques[ataqueAleatorio].nombre
}

function combate() {
    if (ataqueJugador === ataqueEnemigo) {
        textoResultado.innerHTML = `Ambos usaron ${ataqueJugador}. ¡EMPATE! 🤝`
    } else if (
        (ataqueJugador.includes('💧') && ataqueEnemigo.includes('🔥')) ||
        (ataqueJugador.includes('🔥') && ataqueEnemigo.includes('🌱')) ||
        (ataqueJugador.includes('🌱') && ataqueEnemigo.includes('💨')) ||
        (ataqueJugador.includes('💨') && ataqueEnemigo.includes('💧'))
    ) {
        textoResultado.innerHTML = `Usaste ${ataqueJugador}, enemigo usó ${ataqueEnemigo}. ¡RONDA GANADA! 🎉`
        vidasEnemigo--
        spanVidasEnemigo.innerHTML = vidasEnemigo
    } else {
        textoResultado.innerHTML = `Usaste ${ataqueJugador}, enemigo usó ${ataqueEnemigo}. ¡RONDA PERDIDA! 💥`
        vidasJugador--
        spanVidasJugador.innerHTML = vidasJugador
    }

    revisarVidas()
}

function revisarVidas() {
    if (vidasEnemigo === 0) {
        textoResultado.innerHTML = `🏆 ¡Has derrotado a ${enemigoActual.nombre}!`
        finalizarEncuentro(true)
    } else if (vidasJugador === 0) {
        textoResultado.innerHTML = `💀 Has sido derrotado por ${enemigoActual.nombre}.`
        finalizarEncuentro(false)
    }
}

// ----------------------------------------------------------------------------------------------------------
function finalizarEncuentro(ganado) {
    contenedorAtaques.innerHTML = ''

    if (ganado) {
        // Guardar la posición para dejar una calavera 💀
        enemigosDerrotados.push({ x: enemigoActual.x, y: enemigoActual.y })
        enemigosEnMapa = enemigosEnMapa.filter(e => e !== enemigoActual)
        enemigoActual = null
        enCombate = false

        if (enemigosEnMapa.length === 0) {
            // Se revela todo el mapa al derrotar al último enemigo y se abre el baúl
            baul.abierto = true
            revelarTodoElMapa()
            estadoCombate.innerHTML = "🎉 ¡HAS DERROTADO A TODOS LOS ENEMIGOS! El baúl del tesoro se ha abierto. 🎁"
            sectionBotonReiniciar.style.display = 'block'
        } else {
            estadoCombate.innerHTML = "¡Victoria! Sigue explorando para vencer a los demás."
        }
    } else {
        estadoCombate.innerHTML = "Juego Terminado. Pulsa Reiniciar para intentarlo de nuevo."
        sectionBotonReiniciar.style.display = 'block'
    }
}

// ----------------------------------------------------------------------------------------------------------
// Controles y movimientos
function moverDerecha() { if (!enCombate) mascotaJugadorObjeto.velocidadX = 5 }
function moverIzquierda() { if (!enCombate) mascotaJugadorObjeto.velocidadX = -5 }
function moverAbajo() { if (!enCombate) mascotaJugadorObjeto.velocidadY = 5 }
function moverArriba() { if (!enCombate) mascotaJugadorObjeto.velocidadY = -5 }

function detenerMovimiento() {
    if (mascotaJugadorObjeto) {
        mascotaJugadorObjeto.velocidadX = 0
        mascotaJugadorObjeto.velocidadY = 0
    }
}

function sePresionoUnaTecla(event) {
    if (enCombate) return

    switch (event.key) {
        case 'ArrowUp': moverArriba(); break
        case 'ArrowDown': moverAbajo(); break
        case 'ArrowLeft': moverIzquierda(); break
        case 'ArrowRight': moverDerecha(); break
    }
}

// Función para disparar la ráfaga de confeti/papelitos de victoria
function lanzarConfeti() {
    if (typeof confetti === 'function') {
        confetti({
            particleCount: 120,
            spread: 80,
            origin: { y: 0.6 }
        });
        
        // Ráfaga lateral adicional
        setTimeout(() => {
            confetti({
                particleCount: 80,
                angle: 60,
                spread: 55,
                origin: { x: 0 }
            });
            confetti({
                particleCount: 80,
                angle: 120,
                spread: 55,
                origin: { x: 1 }
            });
        }, 2500);
    }
}

// ----------------------------------------------------------------------------------------------------------
// Variable global para controlar que el confeti al tocar el baúl no se repita infinitamente por frame
let tocandoBaulAnterior = false;

// Revisasi el jugador toca el baúl
function revisarColisionBaul() {
    const arribaBaul = baul.y
    const abajoBaul = baul.y + baul.alto
    const derechaBaul = baul.x + baul.ancho
    const izquierdaBaul = baul.x

    const arribaJugador = mascotaJugadorObjeto.y
    const abajoJugador = mascotaJugadorObjeto.y + mascotaJugadorObjeto.alto
    const derechaJugador = mascotaJugadorObjeto.x + mascotaJugadorObjeto.ancho
    const izquierdaJugador = mascotaJugadorObjeto.x

    // Comprobamos si toca el jugador el baúl
    const hayColision = !(
        abajoJugador < arribaBaul ||
        arribaJugador > abajoBaul ||
        derechaJugador < izquierdaBaul ||
        izquierdaJugador > derechaBaul
    );

    if (!hayColision) {
        // Al alejarse, reseteamos el estado para poder volver a activarlo al tocarlo de nuevo
        tocandoBaulAnterior = false;
        return;
    }

    // Si hay colisión:
    if (enemigosEnMapa.length > 0) {
        estadoCombate.innerHTML = "🔒 Debes derrotar a todos los personajes para obtener el tesoro."
    } else {
        // Si no quedan enemigos y aún no estaba abierto, lo abrimos
        if (!baul.abierto) {
            baul.abierto = true
            estadoCombate.innerHTML = "🎁 ¡Has abierto el Baúl del Tesoro y obtenido tu recompensa final!"
            lanzarConfeti()
            tocandoBaulAnterior = true
        } else if (!tocandoBaulAnterior) {
            // Si el baúl ya está abierto y el jugador entra nuevamente en contacto con él, volvemos a celebrar con confeti
            estadoCombate.innerHTML = "🎉 ¡El tesoro es tuyo! Disfruta la victoria. 🎁"
            lanzarConfeti()
            tocandoBaulAnterior = true
        }
    }
}

// ----------------------------------------------------------------------------------------------------------
function finalizarEncuentro(ganado) {
    contenedorAtaques.innerHTML = ''

    if (ganado) {
        // Guardar la posición para dejar una calavera 💀
        enemigosDerrotados.push({ x: enemigoActual.x, y: enemigoActual.y })
        enemigosEnMapa = enemigosEnMapa.filter(e => e !== enemigoActual)
        enemigoActual = null
        enCombate = false

        if (enemigosEnMapa.length === 0) {
            // Se revela todo el mapa al derrotar al último enemigo y se abre el baúl
            baul.abierto = true
            revelarTodoElMapa()
            estadoCombate.innerHTML = "🎉 ¡HAS DERROTADO A TODOS LOS ENEMIGOS! El baúl del tesoro se ha abierto. 🎁"
            sectionBotonReiniciar.style.display = 'block'
            
            lanzarConfeti() // Lanza la explosión de papelitos por ganar el juego
        } else {
            estadoCombate.innerHTML = "¡Victoria! Sigue explorando para vencer a los demás."
        }
    } else {
        estadoCombate.innerHTML = "Juego Terminado. Pulsa Reiniciar para intentarlo de nuevo."
        sectionBotonReiniciar.style.display = 'block'
    }
}


// ----------------------------------------------------------------------------------------------------------
// Iniciar el juego
function iniciarJuego() {
    sectionVerMapa.style.display = 'none'
    sectionBotonReiniciar.style.display = 'none'

    renderizarTarjetasPersonajes()

    botonMascotaJugador.addEventListener('click', seleccionarMascotaJugador)
    botonGenerarPersonajes.addEventListener('click', () => modalGenerar.style.display = 'flex')
    botonConfirmarGenerar.addEventListener('click', generarPersonajes)
    cerrarGenerar.addEventListener('click', () => modalGenerar.style.display = 'none')

    botonReglasInicio.addEventListener('click', () => modalReglas.style.display = 'flex')
    botonReglasMapa.addEventListener('click', () => modalReglas.style.display = 'flex')
    cerrarReglas.addEventListener('click', () => modalReglas.style.display = 'none')

    botonReiniciar.addEventListener('click', () => location.reload())

    window.onclick = function(event) {
        if (event.target === modalReglas) modalReglas.style.display = 'none'
        if (event.target === modalGenerar) modalGenerar.style.display = 'none'
    }
}

// ----------------------------------------------------------------------------------------------------------
function seleccionarMascotaJugador() {
    let inputs = document.querySelectorAll('input[type="radio"]')
    inputs.forEach(input => {
        if (input.checked) {
            mascotaJugador = input.value || input.id
        }
    })

    if (!mascotaJugador) {
        alert('Selecciona un personaje')
        return
    }

    spanMascotaJugador.innerHTML = mascotaJugador
    sectionSeleccionarMascota.style.display = 'none'
    sectionVerMapa.style.display = 'flex'

    mascotaJugadorObjeto = Avatares.find(m => m.nombre === mascotaJugador)
    iniciarMapa()
}

window.addEventListener('load', iniciarJuego)

// ----------------------------------------------------------------------------------------------------------
// FIN
// ----------------------------------------------------------------------------------------------------------