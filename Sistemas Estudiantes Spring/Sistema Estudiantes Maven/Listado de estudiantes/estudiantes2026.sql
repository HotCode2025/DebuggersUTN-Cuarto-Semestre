-- nombre base= estudiantes2026 / nombre id = idestudiantes2026
-- Comenzamos con CRUD: create(insertar), read(leer), update(actualizar), delete(eliminar)
-- Listar los estudiantes(read)
SELECT * FROM estudiantes2026; -- vemos toda la base
-- Insertar estudiante
INSERT INTO estudiantes2026 (nombre, apellido, telefono, email) VALUES("Juan","Perez","2604421840","juanperez@gmail.com");
-- Update (modificar/actualizar) estudiante
UPDATE estudiantes2026 SET nombre ="Juan Carlos", apellido="Garcia" WHERE idestudiantes2026= 1;
-- delete(Eliminar)
DELETE FROM estudiantes2026 WHERE idestudiantes2026=3;
-- mostrar las distintas columnas de la base
SELECT idestudiantes2026 FROM estudiantes2026; -- en este caso vemos la columna id, podemos cambiar el parametro y ver las distintas columnas, o ver mas de una a la vez
-- Para modificar el idestudiantes2026 y que comience desde 1
ALTER TABLE estudiantes2026 AUTO_INCREMENT = 1; -- NO SE ACONSEJA HACERLO, NO ES BUENA PRACTICA, PERO SIRVE












