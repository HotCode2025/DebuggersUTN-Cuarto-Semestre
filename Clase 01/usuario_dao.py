from usuario import Usuario
from conexion import Conexion
from logger_base import log

class UsuarioDAO:
    """
    DAO significa Data ACcess Object
    CRUD significa:
        Create
        Read
        Update
        Delete
    """

    _SELECCIONAR = 'SELECT * FROM usuario ORDER BY id_usuario'
    _INSERTER = 'INSERT INTO usuario (username, password) VALUES (%s, %s)'
    _ACTUALIZAR = 'UPDATE usuario SET username = %s, password = %s WHERE id_usuario = %s'
    _ELIMINAR = 'DELETE FROM usuario WHERE id_usuario = %s'
    _SELECCIONAR_UNO = 'SELECT * FROM usuario WHERE id_usuario = %s'

    # Definimos los metods de clase

    @classmethod
    def seleccionar(cls):
        with Conexion.obtenerConexion() as conexion:
            with Conexion.obtenerCursor() as cursor:
                log.debug('Seleccionando Usuario')
                cursor.execute(cls._SELECCIONAR)
                registros = cursor.fetchall()
                usuarios = [] 
                for registro in registros:
                    usuario = Usuario(registro[0], registro[1], registro[2])
                    usuarios.append(usuario)
                return usuarios

    @classmethod
    def seleccionar_uno(cls, usuario):
        with Conexion.obtenerConexion() as conexion:
            with Conexion.obtenerCursor() as cursor:
                log.debug(f'Seleccionando UN usuario con id: {usuario.id_usuario}')
                valores = (usuario.id_usuario,)  
                cursor.execute(cls._SELECCIONAR_UNO, valores)
                registro = cursor.fetchone()  
                if registro:
                    usuario = Usuario(registro[0], registro[1], registro[2])
                    return usuario
                else:
                    log.debug(f'No se encontró usuario con el ID: {usuario.id_usuario}')
                    return None

    @classmethod
    def insertar(cls, usuario):
        with Conexion.obtenerConexion() as conexion:
            with Conexion.obtenerCursor() as cursor:
                valores = (usuario.username, usuario.password)
                cursor.execute(cls._INSERTER, valores)
                log.debug(f'Usuario Insertado: {usuario}')
                return cursor.rowcount

    @classmethod
    def actualizar(cls, usuario):
        with Conexion.obtenerConexion() as conexion:
            with Conexion.obtenerCursor() as cursor:
                valores = (usuario.username, usuario.password, usuario.id_usuario)
                cursor.execute(cls._ACTUALIZAR, valores)
                log.debug(f'Usuario a actualizar: {usuario}')
                return cursor.rowcount

    @classmethod
    def eliminar(cls, usuario):
        with Conexion.obtenerConexion() as conexion:
            with Conexion.obtenerCursor() as cursor:
                valores = (usuario.id_usuario,)
                cursor.execute(cls._ELIMINAR, valores)
                log.debug(f'Usuario a eliminar: {usuario}')
                return cursor.rowcount

# ----------------------------------------------------------
if __name__ == '__main__':
    # Insertar un registro
    usuario1 = Usuario(username = 'enavarro', password = '147')
    usuario_insertado = UsuarioDAO.insertar(usuario1)
    log.debug(f'Usuario insertado: {usuario_insertado}')

    # actualizar un registro
    usuario1 = Usuario(username = 'acantarelli', password = '258', id_usuario = 5)
    usuario_actualizado = UsuarioDAO.actualizar(usuario1)
    log.debug(f'Usuario insertado: {usuario_actualizado}')

    # Eliminar un registro
    usuario1 = Usuario(id_usuario = 4)
    usuario_eliminado = UsuarioDAO.eliminar(usuario1)
    log.debug(f'Usuario eliminado: {usuario_eliminado}')


    #Seleccionar Objeto
    usuarios = UsuarioDAO.seleccionar()
    for usuario in usuarios:
        log.debug(usuario)
