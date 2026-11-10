console.log("Hola a toda la cohorte 2025");

// Esta funcion se ejecuta de manera asincrona y su funcion es ser un monohilo, es decir, que se va a ejecutar de manera secuencial
var i = 0;
setInterval(function () {
  console.log(i);
  i++;
  //   if (i == 5) {
  //     console.log("Forzamos un error");
  //     var a = 3 + z;
  //   }
}, 1000);
console.log("Segunda instrucción");
