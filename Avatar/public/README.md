# Juego Avatar - Combate por Turnos

Proyecto web interactivo de combate estilo piedra, papel o tijera basado en *Avatar: La leyenda de Aang*. 
Desarrollado con HTML5, CSS3 y JavaScript (ES6+) sin librerías externas.

## Estructura del Proyecto
.
├── css/
│   └── avatar.css       # Estilos, maquetación y variables de tema
├── js/
│   └── avatar.js        # Lógica de juego, eventos y manipulación del DOM
└── avatar.html          # Estructura del juego y modal de reglas

## Detalles Técnicos

* **Gestión del Estado y Variables Globales:** 
Centralización de variables para controlar el conteo de vidas (`vidasJugador`, `vidasEnemigo`), los ataques seleccionados y las referencias directas a los elementos del DOM durante la inicialización del juego (`iniciarJuego`).

* **Variables CSS (`:root`):** Uso de propiedades personalizadas para la paleta de colores, bordes y dimensiones principales (`--card-max-width: 660px`), permitiendo mantenibilidad y cambios de estilo centralizados.

* **Consola de Debug e Historial Dinámico:** Registro e inserción de eventos en tiempo real dentro del elemento `#consola-log` mediante `appendChild`, manteniendo el foco automático en el último turno ejecutando `scrollTop = scrollHeight`.

* **Motor Evaluativo de Combate:** Algoritmo condicional que procesa las victorias, empates y derrotas según las reglas del juego (Patada vence a Puño, Puño a Barrida, Barrida a Patada) y descuenta las vidas de forma reactiva.

* **Ventanas Modales Nativas:** Implementación de la etiqueta HTML5 `<dialog>` para las reglas, manipulada mediante los métodos nativos `.showModal()` y `.close()` de JavaScript.

* **Adaptación Responsiva:** Reordenamiento dinámico de la consola lateral y de la interfaz para pantallas móviles o reducidas mediante la regla `@media (max-width: 1100px)`.

