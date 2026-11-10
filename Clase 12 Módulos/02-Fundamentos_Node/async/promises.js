function hola(nombre) {
  return new Promise(function (resolve, reject) {
    setTimeout(function () {
      console.log("Hola " + nombre);
      resolve(nombre);
    }, 1000);
  });
}

function hablar(nombre) {
  return new Promise(function (resolve, reject) {
    setTimeout(function () {
      console.log("Bla bla bla...");
      //resolve(nombre);
      reject("Hay un error en la función hablar");
    }, 1000);
  });
}

function adios(nombre) {
  return new Promise(function (resolve, reject) {
    setTimeout(function () {
      console.log("Adios " + nombre);
      resolve(nombre);
    }, 1500);
  });
}

// Llamando a las funciones
console.log("Iniciando el proceso...");
hola("Ramiro")
  .then(hablar)
  .then(hablar)
  .then(hablar)
  .then(adios)
  .then((nombre) => {
    console.log("Terminando el proceso...");
  })
  .catch((error) => {
    console.error("Ha ocurrido un error: " + error);
  });
