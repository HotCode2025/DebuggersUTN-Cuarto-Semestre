import { Pool } from "pg";

export const pool = new Pool({
  port: 5432,
  host: "localhost",
  user: "postgres",
  password: "admin",
  database: "PERN",
});

pool.on("connect", () => {
  console.log("Conectado a la base de datos");
});
