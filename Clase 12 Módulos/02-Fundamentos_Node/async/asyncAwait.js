// La palabra async no es necesaria en las funciones porque ya son asincronas, igual proyectan una sincronia visual
async function hola(nombre) {
  return new Promise(function (resolve, reject) {
    setTimeout(function () {
      console.log("Hola " + nombre);
      resolve(nombre);
    }, 1000);
  });
}

async function hablar(nombre) {
  return new Promise(function (resolve, reject) {
    setTimeout(function () {
      console.log("Bla bla bla...");
      //resolve(nombre);
      reject("Hay un error en la función hablar");
    }, 1000);
  });
}

async function adios(nombre) {
  return new Promise(function (resolve, reject) {
    setTimeout(function () {
      console.log("Adios " + nombre);
      resolve(nombre);
    }, 1500);
  });
}

// await hola("Ramiro"); //mala sintaxis
// await solo es valido dentro de funciones async
async function main() {
  let name = await hola("Ramiro");
  await hablar();
  await hablar();
  await hablar();
  await adios(name);
}
console.log("Iniciando el proceso...");

main();

console.log("Terminando el proceso...");
