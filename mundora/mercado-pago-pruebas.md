# MUNDORA · Prueba de pago con Mercado Pago

**Sprint 8 · 3 de noviembre de 2026 · Argentina**  
Integración: Checkout Pro vía API de Orders, con credenciales de prueba.

## Correo del comprador en el checkout

Para reproducir la prueba de MUNDORA, es obligatorio ingresar un correo terminado en **`@testuser.com`** en el campo **E-mail del comprador** del checkout de Mercado Pago. Por ejemplo: `comprador@testuser.com`. Es el correo que se ingresa al pagar; no hace falta cambiar el correo de registro del usuario en Django. Esta indicación corresponde al entorno de prueba del proyecto.

En los intentos anteriores con otro dominio, el checkout no completó el pago y llegó a mostrar «Una de las partes con la que intentás hacer el pago es de prueba». Crear una orden con éxito no indicaba que el pago se hubiera acreditado.

## Evidencia

Con el dominio de prueba, Mercado Pago mostró **«¡Listo! Tu pago ya se acreditó»** por **ARS 13.000** en un pago con Mastercard de prueba. Número de operación: **186550392801**. Este número identifica la operación de pago; no es el Order ID de la API.

## Criterio de cierre

La acreditación en Mercado Pago está comprobada. Para documentar el recorrido completo, comprobar en MUNDORA que la compra correspondiente pasó automáticamente a **confirmada**, que el pedido quedó **en preparación** y que el stock disminuyó solo en la cantidad comprada. Hacer esta observación antes de pulsar «Verificar pago», para distinguir la confirmación automática de la manual. No hace falta generar otro pago.

El test local de verificación duplicada ya pasó: ante dos verificaciones consecutivas de la misma aprobación simulada, el stock pasó de 5 a 4 y permaneció en 4.
