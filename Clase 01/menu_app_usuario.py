from usuario_dao import UsuarioDAO
from logger_base import log
from usuario import Usuario

opcion = None

while opcion != 5:
    print('\n\nMenu APP Manejo de Usuarios')
    print('\nOpciones: ')
    print('1. Listar Usuarios')
    print('2. Agregar Usuario')
    print('3. Modificar Usuario')
    print('4. Eliminar Usuario')
    print('5. Salir')

    try:
        opcion = int(input('Digite una opción (1-5): '))
    except ValueError:
        log.error(f'Opción inválida: {opcion}')
        print('Opción inválida. Debe ingresar un número del 1 al 5')
        opcion = None
        continue

    # ----------------------------------------------------------------------------
    # Listar
    if opcion == 1:
        usuarios = UsuarioDAO.seleccionar()

        # Mostramos los usuario en un formato de columnas
        print('\n' + '=' * 50)
        print('               LISTADO DE USUARIOS')
        print('=' * 50)
        print(f'{"ID":<10} | {"USUARIO":<20} | {"CONTRASEÑA":<15}')
        print('-' * 50)
        if usuarios:
            for usuario in usuarios:
                print(f'{usuario.id_usuario:<10} | {usuario.username:<20} | {usuario.password:<15}')
        else:
            print('No hay usuarios registrados.')
        print('=' * 50)
        input('\nPresione ENTER para continuar')
    # ----------------------------------------------------------------------------
    # Agregar
    elif opcion == 2:
        nombre = input('Ingrese el nombre del usuario: ')
        clave  = input('Ingrese la clave del usuario: ')
        usuario_nuevo = Usuario(username = nombre, password = clave)
        usuario = UsuarioDAO.insertar(usuario_nuevo)
        log.info(f'Usuario insertado: {usuario_nuevo}')
        print(f'Usuario insertado: Usuario: {usuario_nuevo.username} | Clave: {usuario_nuevo.password}')
        input('Presione ENTER para continuar')
    # ----------------------------------------------------------------------------
    # Modificar
    elif opcion == 3:
        try:
            id = int(input('Ingrese el ID del usuario: '))
        except ValueError:
            log.error('ID inválido. Debe ingresar un número entero')
            input('Presione ENTER para continuar')
            id = None
            continue  
        # Si el Id es un numero entero continuo
        usuario_a_buscar = Usuario(id_usuario=id)
        usuario_encontrado = UsuarioDAO.seleccionar_uno(usuario_a_buscar)
        if usuario_encontrado:
            log.info(f'Usuario a modificar: {usuario_encontrado}')
            print(f'Usuario a modificar: ID: {usuario_encontrado.id_usuario} | Usuario: {usuario_encontrado.username} | Clave: {usuario_encontrado.password}')
            confirmacion = input('¿Está seguro de que desea modificar este usuario? (S/N): ')
            if confirmacion == 's':
                nombre = input('Ingrese el nombre del usuario: ')
                clave  = input('Ingrese la clave del usuario: ')
                usuario_modificar = Usuario(id_usuario = id, username = nombre, password = clave)
                usuario = UsuarioDAO.actualizar(usuario_modificar)
                log.info(f'Usuario modificado: {usuario_modificar}')
                print(f'Usuario modificado: ID: {usuario_modificar.id_usuario} | Usuario: {usuario_modificar.username} | Clave: {usuario_modificar.password}')
                input('Presione ENTER para continuar')
            else:
                log.info('El usuario no fue modificado.')
                print('El usuario no fue modificado.')
                input('Presione ENTER para continuar')
        else:
            log.debug(f'El usuario buscado ID = {id} no existe')
            print(f'El usuario buscado ID = {id} no existe')
            input('Presione ENTER para continuar')
    # ----------------------------------------------------------------------------
    # Eliminar
    elif opcion == 4:
        try:
            id = int(input('Ingrese el ID del usuario: '))
        except ValueError:
            log.error('ID inválido. Debe ingresar un número entero')
            input('Presione ENTER para continuar')
            id = None
            continue  
        # Si el Id es un numero entero continuo
        usuario_a_buscar = Usuario(id_usuario=id)
        usuario_encontrado = UsuarioDAO.seleccionar_uno(usuario_a_buscar)
        if usuario_encontrado:
            log.info(f'Usuario a eliminar: {usuario_encontrado}')
            print(f'Usuario a eliminar: ID: {usuario_encontrado.id_usuario} | Usuario: {usuario_encontrado.username} | Clave: {usuario_encontrado.password}')
            confirmacion = input('¿Está seguro de que desea eliminar este usuario? (S/N): ')
            
            if confirmacion == 's':
                usuario = UsuarioDAO.eliminar(usuario_encontrado)
                log.info(f'Usuario eliminado: {usuario_encontrado}')
                print(f'Usuario eliminado: {usuario_encontrado}')
                input('Presione ENTER para continuar')
            else:
                log.info('El usuario no fue eliminado.')
                print('El usuario no fue eliminado.')
                input('Presione ENTER para continuar')
        else:
            log.debug(f'El usuario buscado ID = {id} no existe')
            print(f'El usuario buscado ID = {id} no existe')
            input('Presione ENTER para continuar')

# ----------------------------------------------------------------------------
# Salir
else:
    log.info('\nSalimos del menú')
