const cartBtn = document.getElementById("cart-btn");
const modalOverlay = document.getElementById("modal-overlay");
const modalContainer = document.getElementById("modal-container");

const openModal = () => {
  modalOverlay.style.display = "block";
  modalContainer.style.display = "block";
};

const closeModal = () => {
  modalOverlay.style.display = "none";
  modalContainer.style.display = "none";
};

const renderCart = () => {
  modalContainer.innerHTML = "";

  const modalHeader = document.createElement("div");
  modalHeader.innerHTML = `
    <div class="modal-close" id="modal-close">❌</div>
    <div class="modal-title">Carrito</div>
  `;
  modalContainer.append(modalHeader);

  const modalBody = document.createElement("div");
  modalBody.className = "modal-body";

  if (cart.length === 0) {
    modalBody.innerHTML = "<p>El carrito está vacío</p>";
  }

  cart.forEach((product) => {
    const item = document.createElement("div");
    item.className = "product";
    item.innerHTML = `
      <img class="product-img" src="${product.img}" alt="${product.productName}">
      <div class="product-info">
        <h4>${product.productName}</h4>
      </div>
      <div class="quantity">
        <span class="quantity-btn-decrese" data-id="${product.id}">-</span>
        <input class="quantity-input" type="text" value="${product.quanty}" readonly>
        <span class="quantity-btn-increase" data-id="${product.id}">+</span>
      </div>
      <div class="price">${product.price * product.quanty} $</div>
      <div class="delete-product" data-id="${product.id}">❌</div>
    `;
    modalBody.append(item);
  });
  modalContainer.append(modalBody);

  const total = cart.reduce((acc, p) => acc + p.price * p.quanty, 0);
  const modalFooter = document.createElement("div");
  modalFooter.className = "modal-footer";
  modalFooter.innerHTML = `<div class="total-price">Total: ${total} $</div>`;
  modalContainer.append(modalFooter);
};

cartBtn.addEventListener("click", () => {
  renderCart();
  openModal();
});

modalOverlay.addEventListener("click", closeModal);

modalContainer.addEventListener("click", (e) => {
  const target = e.target;
  const id = Number(target.dataset.id);

  if (target.id === "modal-close") {
    closeModal();
    return;
  }

  if (target.classList.contains("quantity-btn-decrese")) {
    const item = cart.find((p) => p.id === id);
    if (item && item.quanty > 1) {
      item.quanty--;
      saveCart();
      renderCart();
    }
  } else if (target.classList.contains("quantity-btn-increase")) {
    const item = cart.find((p) => p.id === id);
    if (item) {
      item.quanty++;
      saveCart();
      renderCart();
    }
  } else if (target.classList.contains("delete-product")) {
    cart = cart.filter((p) => p.id !== id);
    saveCart();
    renderCart();
  }
});
