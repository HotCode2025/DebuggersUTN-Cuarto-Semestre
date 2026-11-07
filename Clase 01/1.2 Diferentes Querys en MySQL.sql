-- Comenzamos con CRUD: create(insertar), read(leer), update(actualizar), delete(eliminar)
-- Listar los estudiantes (read)
SELECT * FROM estudiantes2026;
-- Insertar estudiante
INSERT INTO estudiantes2026 (nombre, apellido, telefono, email) VALUES ("Juan", "Perez", "2614545456", "juan@mail.com");
-- Update (modificar)
UPDATE estudiantes2026 SET nombre="Juan Carlos", apellido="Garcia" WHERE idestudiantes2026= 1;
-- Delete(eliminar)
DELETE FROM estudiantes2026 WHERE idestudiantes2026=1;
-- Para modificar el idestudiantes2026 y comience en 1
ALTER TABLE estudiantes2026 AUTO_INCREMENT = 1;