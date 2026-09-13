const shopContent = document.getElementById("shopContent");
const cart = [];

productos.forEach(product => {
    const content = document.createElement("div");
    content.innerHTML = `
        <img src="${product.img}">
        <h3>${product.productName}</h3>
        <p>$ ${product.price}</p>
    `;
    shopContent.append(content);

    const buyBotton = document.createElement("button");
    buyBotton.innerHTML = "Comprar";

    content.append(buyBotton);

    buyBotton.addEventListener("click", () => {
        const repeat = cart.some((repeatProduct) => repeatProduct.id === product.id);
        if (repeat) {
            cart.map((prod) => {
                if (prod.id === product.id) {
                    prod.quanty++;
                    displayCartCounter();
                }
            });
        }
        else {
            cart.push({
                id: product.id,
                productName: product.productName,
                price: product.price,
                quanty: product.quanty,
                img: product.img,
            });
            displayCartCounter();
        }
        console.log(cart);
    });
});

// -------------------------------------------------------------------------------------------
// Verifica la condicion que nos devuelve mercadopago sobre el resultado de la operacion 

document.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    const status = urlParams.get("status");
    const paymentId = urlParams.get("payment_id");

    if (status === "approved" && paymentId) {
        // Vaciar el carrito en memoria
        cart.length = 0;
        if (typeof displayCartCounter === "function") {
            displayCartCounter();
        }

        // Mostrar la ventana emergente de éxito
        showSuccessModal(paymentId);

        // Limpiar los parámetros de la URL para evitar re-disparar el aviso al recargar
        window.history.replaceState({}, document.title, window.location.pathname);
    } else if (status === "failure" || status === "rejected") {
        showErrorModal();
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});

// Ventana de pago correcto
function showSuccessModal(paymentId) {
    const modalContainer = document.getElementById("modal-container");
    const modalOverlay = document.getElementById("modal-overlay");

    if (!modalContainer || !modalOverlay) return;

    modalContainer.innerHTML = `
        <div class="modal-header" style="text-align: center; padding: 20px 10px 0;">
            <h1 style="font-size: 1.5rem; color: #e2e0e0ff; margin: 0; font-weight: bold;">Debuggers UTN Tienda Online</h1>
            <h2 style="color: #2e7d32; font-size: 1.25rem; margin-top: 8px;">¡Gracias por tu compra!</h2>
        </div>
        <div class="modal-body" style="text-align: center; padding: 15px;">
            <p>Tu pago ha sido procesado exitosamente por Mercado Pago.</p>
            <p style="background: #e8f5e9; padding: 10px; border-radius: 8px; font-weight: bold; color: #1b5e20;">
                N° de Pago / Comprobante: ${paymentId}
            </p>
            <p>Se ha registrado tu operación en el sistema.</p>
        </div>
        <div class="modal-footer" style="text-align: center; padding: 15px;">
            <button id="close-success-btn" class="btn-primary" style="background-color: #2e7d32; cursor: pointer; padding: 10px 20px; border: none; color: white; border-radius: 5px; font-weight: bold;">
                Volver a la tienda
            </button>
        </div>
    `;

    modalContainer.style.display = "block";
    modalOverlay.style.display = "block";

    document.getElementById("close-success-btn").addEventListener("click", () => {
        modalContainer.style.display = "none";
        modalOverlay.style.display = "none";
    });
}

// Ventana de Error
function showErrorModal() {
    const modalContainer = document.getElementById("modal-container");
    const modalOverlay = document.getElementById("modal-overlay");

    if (!modalContainer || !modalOverlay) return;

    modalContainer.innerHTML = `
        <div class="modal-header" style="text-align: center; padding: 20px 10px 0;">
            <h1 style="font-size: 3rem; margin: 0;">❌</h1>
            <h2 style="color: #c62828; margin-top: 10px;">Pago no completado</h2>
        </div>
        <div class="modal-body" style="text-align: center; padding: 15px;">
            <p>Ocurrió un problema al procesar la transacción o la operación fue cancelada.</p>
        </div>
        <div class="modal-footer" style="text-align: center; padding: 15px;">
            <button id="close-error-btn" class="btn-primary" style="background-color: #c62828; cursor: pointer; padding: 10px 20px; border: none; color: white; border-radius: 5px; font-weight: bold;">
                Entendido
            </button>
        </div>
    `;

    modalContainer.style.display = "block";
    modalOverlay.style.display = "block";

    document.getElementById("close-error-btn").addEventListener("click", () => {
        modalContainer.style.display = "none";
        modalOverlay.style.display = "none";
    });
}
