import logging as log
import os

# Esto nos permite obtener la ruta del directorio donde se encuentra el proyecto
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_LOG = os.path.join(DIRECTORIO_ACTUAL, 'capa_datos.log')

# Configuracion basica de logging
log.basicConfig(
    level=log.INFO,
    format='%(asctime)s: %(levelname)s [%(filename)s: %(lineno)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %p',
    handlers=[
        log.FileHandler(RUTA_LOG, encoding='utf-8'), 
#        log.StreamHandler() # al eliminar esta linea los log no se muestran en pantalla
    ]
)

if __name__ == '__main__':
    log.debug('Mensaje a nivel debug')
    log.info('Mensaje a nivel info')
    log.warning('Mensaje a nivel warning')
    log.error('Mensaje a nivel error')
    log.critical('Mensaje a nivel critical')
