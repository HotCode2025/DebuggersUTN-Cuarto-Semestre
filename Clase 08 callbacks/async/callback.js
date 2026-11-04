/*
function soyAsincrona(miCallback) {
    setTimeout(function() {
        console.log('Hola, soy una funcion asincrona');
        miCallback();
    }, 1000);
}

console.log('Iniciando el proceso....');
soyAsincrona(function(){
    console.log('Terminando el proceso....');
});
*/

function hola(nombre, miCallback) {
    setTimeout(function() {
        console.log('Hola ' + nombre);
        miCallback('Carlos');
    }, 1000);
}

function adios(nombre, otroCallback) {
    setTimeout(function() {
        console.log('Adios ' + nombre);
        otroCallback();
    }, 1000);
}

console.log('Iniciando el proceso....');
/*
hola('Carlos', function(){
    adios('Carlos', function() {
        console.log('Terminando el proceso....');
    });
});
*/

// hola('Carlos', function() {});
// adios('Carlos', function() {});

hola('Carlos', function(nombre){
    adios(nombre, function() {
        console.log('Terminando el proceso....');
    });
});
