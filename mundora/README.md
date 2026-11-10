# MUNDORA
**Diseño argentino, para tu día a día.**

Proyecto académico de Debuggers UTN: una tienda online de productos de diseño para el hogar, con múltiples vendedores, carrito, entrega por tienda y pagos de prueba con Mercado Pago.

## Tecnologías
Python, Django, MySQL, HTML, CSS y JavaScript. Las dependencias están en requirements.txt. El entorno del desarrollo utilizó Python 3.14.

## Instalación local en Windows
Abrí PowerShell en la carpeta del proyecto que contiene manage.py.

### 1. Entorno virtual
```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
Si la activación está bloqueada, ejecutá en esa terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```
Después repetí la activación.

### 2. Base de datos
Iniciá MySQL. Para una instalación nueva, ejecutá con un usuario administrador:
```sql
CREATE DATABASE mundora CHARACTER SET utf8mb4;
CREATE USER 'mundora_app'@'localhost' IDENTIFIED BY 'REEMPLAZAR_CON_TU_CLAVE';
GRANT ALL PRIVILEGES ON mundora.* TO 'mundora_app'@'localhost';
```
Elegí tu contraseña antes de ejecutar el bloque. Si la base y el usuario existen, utilizá sus datos.

### 3. Variables locales
Solo si todavía no tenés .env:
```powershell
Copy-Item .env.example .env
```
Generá una clave:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Pegala entre comillas simples en DJANGO_SECRET_KEY. Completá DB_PASSWORD y revisá las demás variables de MySQL. Usá DJANGO_DEBUG=True para desarrollo. Cada línea tiene formato NOMBRE=valor. No publiques .env ni las credenciales.

### 4. Inicialización
```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Abrí http://127.0.0.1:8000/ y http://127.0.0.1:8000/admin/ para administrar.
Una base nueva queda sin productos: las migraciones crean tablas, no datos de demostración. Prepará categorías, una tienda y productos con imágenes, variantes activas y stock.

## Usuarios
- Comprador: registro, acceso con usuario o correo, perfil, domicilio, carrito y seguimiento desde Mis compras.
- Vendedor: productos, variantes, galería y pedidos desde Mi cuenta → Panel del vendedor.
- Administrador: revisión de tiendas y publicaciones desde el administrador de Django.

## Pagos de prueba
Esta sección es necesaria para probar pagos; no para recorrer el catálogo.
1. Configurá una aplicación de Mercado Pago Developers con credenciales de prueba.
2. En .env completá MP_ACCESS_TOKEN_PRUEBA y MP_WEBHOOK_SECRETO_PRUEBA. El Access Token y el secreto de firma de webhooks son valores distintos.
3. Con ngrok instalado y autenticado, ejecutá en otra terminal:
```powershell
ngrok http 8000
```
4. Copiá el dominio del túnel en NGROK_HOST, sin https:// ni barra final. Django debe admitirlo en ALLOWED_HOSTS. Reiniciá Django al modificar las variables locales.
5. En Mercado Pago configurá el webhook de prueba para Order (Mercado Pago), con la URL https://TU-DOMINIO/compras/mercado-pago/webhook/. Si cambia el dominio, actualizalo en ambos lugares.
6. Abrí MUNDORA desde el dominio del túnel antes de iniciar sesión para conservar esa sesión al volver del checkout.
7. Agregá un producto, elegí envío o retiro por tienda y continuá al pago. Usá tarjeta y datos de prueba.
8. En las pruebas de MUNDORA, el correo ingresado en el checkout debió terminar en @testuser.com. No hace falta cambiar el correo del perfil local.

El resultado esperado es compra confirmada y pedido en preparación. La respuesta 201 Created solo indica creación de la orden: no acredita el pago. El retorno del navegador muestra la compra; el webhook permite verificar la acreditación en el servidor.

## Diagnóstico de pagos
- 400 / DisallowedHost: revisar el dominio del túnel en ALLOWED_HOSTS.
- 401 / Firma no válida: revisar el secreto de webhooks de prueba. La validación de MUNDORA utiliza el ID alfanumérico en minúsculas para calcular la firma.
- Pago acreditado pero compra pendiente: consultar el estado mediante Verificar pago antes de generar otro pago.
- Túnel cerrado: volver a ejecutar ngrok http 8000 y revisar si cambió el dominio.

## Alcance de la demostración
El envío se cotiza con un simulador propio. Los pagos están configurados para pruebas, y el túnel no es un despliegue permanente. Las cancelaciones y devoluciones con reembolso simulado no representan movimientos de dinero real.
