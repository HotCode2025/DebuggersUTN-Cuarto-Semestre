const modalContainer = document.getElementById("modal-container");
const modalOverlay = document.getElementById("modal-overlay");
const cartBtn = document.getElementById("cart-btn");
const cartCounter = document.getElementById("cart-counter");

const displayCart = () => {
    modalContainer.innerHTML = "";
    modalContainer.style.display = "block";
    modalOverlay.style.display = "block";

    // modal header
    const modalHeader = document.createElement("div");
    const modalClose = document.createElement("div");
    modalClose.innerText = "❌";
    modalClose.className = "modal-close";
    modalHeader.append(modalClose);

    modalClose.addEventListener("click", () => {
        modalContainer.style.display = "none"
        modalOverlay.style.display = "none"
    });

    modalContainer.style.display = "block";
    modalOverlay.style.display = "block";

    const modalTitle = document.createElement("div");
    modalTitle.innerText = "Carrito";
    modalTitle.className = "modal-title";
    modalHeader.append(modalTitle);
    modalContainer.append(modalHeader);

    // modal body
    if (cart.length > 0) {
        cart.forEach((product) => {
            const modalBody = document.createElement("div");
            modalBody.className = "modal-body";
            modalBody.innerHTML = `
                <div class="product">
                    <img class="product-img" src="${product.img}" />
                    <div class="produc-info">
                        <h4>${product.productName}</h4>
                    </div>
                    <div class="quantity">
                        <span class="quantity-btn-decrese">➖</span>
                        <span class="quantity-input">${product.quanty}</span>
                        <span class="quantity-btn-increse">➕</span>
                    </div>
                    <div class="price">$ ${product.price * product.quanty}</div>
                    <div class="delete-product">❌</div>
                </div>
            `;
            modalContainer.append(modalBody);

            const decrese = modalBody.querySelector(".quantity-btn-decrese");
            decrese.addEventListener("click", () => {
                if (product.quanty !== 1) {
                    product.quanty--;
                    displayCart();
                }
                displayCartCounter();
            });

            const increse = modalBody.querySelector(".quantity-btn-increse");
            increse.addEventListener("click", () => {
                product.quanty++;
                displayCart();
                displayCartCounter();
            });

            // Eliminar producto del carrito
            const deleteProduct = modalBody.querySelector(".delete-product");
            deleteProduct.addEventListener("click", () => {
                deleteCartProduct(product.id);
            })
        }); // Fin cart.forEach((product) => {

        // modal footer
        const total = cart.reduce((acc, el) => acc + el.price * el.quanty, 0);

        const modalFooter = document.createElement("div");
        modalFooter.className = "modal-footer";
        modalFooter.innerHTML = `
            <div class="total-price">Total: $ ${total}</div>
            <button class="btn-primary" id="checkout-btn"> Pagar </button>
            <div id="button-checkout"></div>
        `;
        modalContainer.append(modalFooter);

        // Mercado pago
        const mercadopago = new MercadoPago("APP_USR-b2cc738f-99d2ed0e722c", {
            locale: "es-AR",
        });

        const checkoutButton = modalFooter.querySelector("#checkout-btn");
        
        checkoutButton.addEventListener("click", function () {
            checkoutButton.remove();

            const orderData = {
                quantity: 1,
                description: "compra de ecommerce",
                price: total,
            };

            fetch("http://localhost:8080/create_preference", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(orderData),
            })
            .then(async function(response) {
                if (!response.ok) {
                    // Captura el texto o JSON enviado por el servidor ante un status 400, 403 o 500
                    const errorText = await response.text();
                    throw new Error(`HTTP ${response.status}: ${errorText}`);
                }
                return response.json();
            })
            .then(function(preference) {
                createCheckoutButton(preference.id);
            })
            .catch(function(error) {
                console.error("Detalle técnico del error:", error);
                alert("Ocurrió un error: " + error.message);
            });
        });

        function createCheckoutButton(preferenceId) {
            // Inicializa checkout
            const bricksBuilder = mercadopago.bricks();

            const renderComponent = async (bricksBuilder) => {
                const container = document.getElementById("button-checkout");
                if (container) {
                    container.innerHTML = "";
                }

                await bricksBuilder.create (
                    "wallet",
                    "button-checkout",
                    {
                        initialization: {
                            preferenceId: preferenceId,
                        },
                        callbacks: {
                            onError: (error) => console.error(error),
                            onReady: () => {},
                        },
                    }
                );
            };
            window.checkoutButton = renderComponent(bricksBuilder);
        }
    }
    else {
        const modalText = document.createElement("h2");
        modalText.className = "modal-body";
        modalText.innerText = "Su carrito esta vacio";
        modalContainer.append(modalText);
    }
};

cartBtn.addEventListener("click", displayCart);

const deleteCartProduct = (id) => {
    const foundId = cart.findIndex((element) => element.id === id);
    cart.splice(foundId, 1);
    displayCart();
    displayCartCounter();
}

const displayCartCounter = () => {
    const cartLength = cart.reduce((acc, el) => acc + el.quanty, 0);
    if (cartLength > 0) {
        cartCounter.style.display = "block";
        cartCounter.innerText = cartLength;
    }
    else {
        cartCounter.style.display = "none";
    }
}
