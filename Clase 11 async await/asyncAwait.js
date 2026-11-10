//La palabra async no es necesaria en las funciones, porque ya son asincronas
//Igual proyactan una asincronia visual
async function hola(nombre){
    return new Promise(function (resolve, reject) {
        setTimeout( function () {
            console.log('hola '+nombre);
            resolve(nombre);
        }, 1000);
    });
}

async function hablar(nombre){
    return new Promise( (resolve, reject) => { //usamos la sintaxis ES6
        setTimeout( function () {
            console.log('bla bla bla bla');
            resolve(nombre);
        }, 1000);
    });
}

async function adios(nombre) {
    return new Promise( (resolve, reject) => {
        setTimeout( function() {
            //validamos el error o aprobación
            console.log('Adios '+nombre);
            //if(err) reject('Hay un error');
            resolve();
        }, 1000);
    });
}

//await hola('Kevin'); esto es una mala sintaxis
// await solo es valido dentro de una funcion asincrona

async function main(){
    let nombre = await hola('Kevin');
    await hablar();
    await hablar();
    await hablar();
    await adios(nombre);
    console.log('Termina el proceso...')
}

console.log('Empezamos el proceso...')
main();
console.log('Esta va a ser la segunda instrucción')

//Codigo en Ingles

 // The word async is not necessary in the functions because they are already asynchronous
// They still provide a visual representation of asynchrony
async function hello(name) {
    return new Promise(function (resolve, reject) {
        setTimeout(function () {
            console.log('hello ' + name);
            resolve(name);
        }, 1000);
    });
}

async function talk(name) {
    return new Promise((resolve, reject) => { // We use ES6 syntax
        setTimeout(function () {
            console.log('blah blah blah blah');
            resolve(name);
        }, 1000);
    });
}

async function goodbye(name) {
    return new Promise((resolve, reject) => {
        setTimeout(function () {
            // Validate the error or approval
            console.log('Goodbye ' + name);
            // if (err) reject('There is an error');
            resolve();
        }, 1000);
    });
}

// await hello('Kevin'); this is incorrect syntax
// await is only valid inside an asynchronous function

async function main() {
    let name = await hello('Kevin');
    await talk();
    await talk();
    await talk();
    await goodbye(name);
    console.log('The process has finished...');
}

console.log('Starting the process...');
main();
console.log('This will be the second instruction');
