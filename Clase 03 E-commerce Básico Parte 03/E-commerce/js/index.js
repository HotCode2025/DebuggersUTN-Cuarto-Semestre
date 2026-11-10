const shopContent = document.getElementById("shopContent");

let cart = [];
try {
  cart = JSON.parse(localStorage.getItem("cart")) || [];
} catch (e) {
  cart = [];
}

const saveCart = () => {
  try {
    localStorage.setItem("cart", JSON.stringify(cart));
  } catch (e) {
    /* sin almacenamiento disponible: el carrito vive solo en memoria */
  }
};

products.forEach((product) => {
  const content = document.createElement("div");
  content.innerHTML = `
    <img src="${product.img}" alt="${product.productName}">
    <h3>${product.productName}</h3>
    <p>${product.price} $</p>
  `;
  shopContent.append(content);

  const buyButton = document.createElement("button");
  buyButton.innerText = "Comprar";
  content.append(buyButton);

  buyButton.addEventListener("click", () => {
    const repeat = cart.some((item) => item.id === product.id);

    if (repeat) {
      cart = cart.map((item) =>
        item.id === product.id ? { ...item, quanty: item.quanty + 1 } : item
      );
    } else {
      cart.push({
        id: product.id,
        productName: product.productName,
        price: product.price,
        quanty: 1,
        img: product.img,
      });
    }
    saveCart();
  });
});
