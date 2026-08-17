from persona import Persona
from conexion import Conexion
from logger_base import log

class PersonaDAO:
    """
    DAO significa Data ACcess Object
    CRUD significa:
        Create
        Read
        Update
        Delete
    """

    _SELECCIONAR = 'SELECT * FROM persona ORDER BY id_persona'
    _INSERTER = 'INSERT INTO persona (nombre, apellido, email) VALUES (%s, %s, %s)'
    _ACTUALIZAR = 'UPDATE persona SET nombre = %s, apellido = %s, email = %s WHERE id_persona = %s'
    _ELIMINAR = 'DELETE FROM persona WHERE id_persona = %s'

    # Definimos los metods de clase

    @classmethod
    def seleccionar(cls):
        # El context manager de la conexion administra la transaccion
        with Conexion.obtenerConexion() as conexion:
            # El context manager del cursor asegura que se cierre al terminar este bloque
            with Conexion.obtenerCursor() as cursor:
                cursor.execute(cls._SELECCIONAR)
                registros = cursor.fetchall()
                personas = [] 
                for registro in registros:
                    persona = Persona(registro[0], registro[1], registro[2], registro[3])
                    personas.append(persona)
                return personas
            
    @classmethod
    def insertar(cls, persona):
        with Conexion.obtenerConexion() as conexion:
            with Conexion.obtenerCursor() as cursor:
                valores = (persona.nombre, persona.apellido, persona.email)
                cursor.execute(cls._INSERTER, valores)
                log.debug(f'Persona Insertada: {persona}')
                return cursor.rowcount

# ----------------------------------------------------------
if __name__ == '__main__':
    # Insertar un registro
    persona1 = Persona(nombre = 'Pedro', apellido = 'Romero', email = 'promero@mail.com')
    personas_insertadas = PersonaDAO.insertar(persona1)
    log.debug(f'Personas insertadas: {personas_insertadas}')

    #Seleccionar Objeto
    personas = PersonaDAO.seleccionar()
    for persona in personas:
        log.debug(persona)

