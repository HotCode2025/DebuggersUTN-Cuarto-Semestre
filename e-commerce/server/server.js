const express = require("express");
const app = express();
const cors = require("cors");
const path = require("path");

const { MercadoPagoConfig, Preference } = require("mercadopago");

// Access Token de Mercado Pago
const client = new MercadoPagoConfig({
  accessToken: "APP_USR-6425965593051519-6225c8bcf5502f4df076b7a5fd342133",
});

app.use(cors());
app.use(express.urlencoded({ extended: false }));
app.use(express.json());

// Servir archivos estáticos del cliente
app.use(express.static(path.join(__dirname, '../client')));

// Rutas API (van antes de la ruta catch-all '*')
app.post("/create_preference", async (req, res) => {
    try {
        const preference = new Preference(client);
        const result = await preference.create({
            body: {
            items: [
                {
                title: req.body.description,
                unit_price: Number(req.body.price),
                quantity: Number(req.body.quantity),
                },
            ],
            back_urls: {
                success: "http://localhost:8080/",
                failure: "http://localhost:8080/",
                pending: "",
            },
            //auto_return: "approved",
            },
        });

        // Devuelve el id de la preferencia creada
        res.json({ id: result.id });
    } 
    catch (error) {
        console.error("Error al crear la preferencia:", error);
        res.status(500).send("Error al crear la preferencia");
    }
});

app.get("/feedback", function (req, res) {
  res.json({
    Payment: req.query.payment_id,
    Status: req.query.status,
    MerchantOrder: req.query.merchant_order_id,
  });
});

// Ruta Catch-all para el SPA / frontend
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/index.html'));
});

// Inicio del servidor
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Servidor escuchando en http://localhost:${PORT}`);
});
