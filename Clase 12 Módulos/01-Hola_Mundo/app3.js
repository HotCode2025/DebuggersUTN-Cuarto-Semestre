console.log("Inicio de programa");
setTimeout(() => {
  console.log("Primer setTimeout");
}, 3000);
setTimeout(() => {
  console.log("Segundo setTimeout");
}, 0);
setTimeout(() => {
  console.log("Tercero setTimeout");
}, 0);
console.log("Fin de programa");
