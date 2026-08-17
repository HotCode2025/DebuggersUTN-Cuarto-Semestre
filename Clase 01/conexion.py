import os
# FORZAR IDIOMA ANTES DE IMPORTAR PSYCOPG2
os.environ['LC_ALL'] = 'C'
os.environ['LC_MESSAGES'] = 'English'
os.environ['LANG'] = 'en_US.UTF-8'

import psycopg2 as bd
from logger_base import log
import sys

class Conexion:
    _DATABASE = 'programacion_iv'
    _USERNAME = 'postgres'
    _PASSWORD = 'olimpo12'
    _DB_PORT = '5432'
    _HOST = '127.0.0.1'
    _conexion = None
    _cursor = None
    

    @classmethod
    def obtenerConexion(cls):
        if cls._conexion is None:
            try:
                cls._conexion = bd.connect(host = cls._HOST,
                                            user = cls._USERNAME,
                                            password = cls._PASSWORD,
                                            port = cls._DB_PORT,
                                            database = cls._DATABASE
                                            )
                
                log.debug(f'Conexion Exitosa: {cls._conexion}')
                return cls._conexion
            except Exception as e:
                log.error(f'Ocurrio un error real: {repr(e)}')
                sys.exit()
        else:
            return cls._conexion

    @classmethod
    def obtenerCursor(cls):
        try:
            cursor = cls.obtenerConexion().cursor()
            log.debug(f'Se abrio correctamente el cursor: {cursor}')
            return cursor
        except Exception as e:
            log.error(f'Ocurrio un error al obtener el cursor: {e}')
            sys.exit()

if __name__ == '__main__':
    Conexion.obtenerConexion()
    Conexion.obtenerCursor()

