import express from "express";
import morgan from "morgan";
import tareasRoutes from "./router/tareas.routes.js";
import authRoutes from "./router/auth.routes.js";
import cookieParser from "cookie-parser";

const app = express(); // Creamos una instancia de express
// Middlewares
app.use(morgan("dev")); // Esto es para ver las peticiones en la consola
app.use(cookieParser()); // Esto es para que express entienda las cookies
app.use(express.json()); // Esto es para que express entienda el json
app.use(express.urlencoded({ extended: false })); // Esto es para que express entienda el urlencoded, se utiliza para enviar formularios

app.get("/", (req, res) => res.json({ message: "Bienvenidos a mi proyecto" })); // Creamos una ruta para la raiz del servidor que responde con un json con un mensaje de bienvenida
app.use("/api", tareasRoutes); // Creamos una ruta para las tareas
app.use("/api", authRoutes); // Creamos una ruta para el auth

// Manejo de errores
app.use((err, req, res, next) => {
  res.status(500).json({
    status: "error",
    message: err.message,
  });
});

export default app; // Exportamos la app
