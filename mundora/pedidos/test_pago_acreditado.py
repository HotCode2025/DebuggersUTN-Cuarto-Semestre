"""Comprueba el efecto de dos verificaciones del mismo pago en la base de pruebas."""
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from catalog.models import Categoria, ImagenProducto, Producto, Tienda, Variante
from pedidos.models import Compra, DetallePedido, Pedido
from pedidos.verificacion import verificar_pago_de_compra


class PagoAcreditadoTest(TestCase):
    """Prueba la verificación compartida por el webhook y el botón del comprador."""

    def test_dos_verificaciones_descontando_una_sola_unidad(self):
        usuario = get_user_model()
        comprador = usuario.objects.create_user(username="compra_test", email="compra@example.com")
        vendedor = usuario.objects.create_user(username="vende_test", email="vende@example.com")
        tienda = Tienda.objects.create(propietario=vendedor, nombre="Taller de prueba",
                                      estado=Tienda.Estado.APROBADA)
        categoria = Categoria.objects.create(nombre="Luces", identificador_url="luces")
        producto = Producto.objects.create(tienda=tienda, categoria=categoria, nombre="Velador",
                                           identificador_url="velador", publicado=True,
                                           estado_revision=Producto.EstadoRevision.APROBADO)
        ImagenProducto.objects.create(producto=producto, imagen="pruebas/velador.jpg",
                                      texto_alternativo="Velador de prueba")
        variante = Variante.objects.create(producto=producto, precio=Decimal("10000.00"), stock=5)
        compra = Compra.objects.create(comprador=comprador, mp_orden_id="ORDTSTLOCAL")
        pedido = Pedido.objects.create(compra=compra, tienda=tienda, nombre_tienda=tienda.nombre,
                                       modalidad_entrega=Pedido.ModalidadEntrega.ENVIO,
                                       costo_entrega=Decimal("3000.00"))
        DetallePedido.objects.create(pedido=pedido, variante=variante, cantidad=1,
                                     nombre_producto=producto.nombre, precio_unitario=variante.precio)

        self.assertEqual(compra.estado, Compra.Estado.PENDIENTE)
        self.assertEqual(compra.total_con_entrega, Decimal("13000.00"))
        respuesta = {
            "id": compra.mp_orden_id, "external_reference": str(compra.codigo),
            "status": "processed", "status_detail": "accredited", "currency": "ARS",
            "total_paid_amount": "13000.00", "total_amount": "13000.00",
        }

        # Solo se sustituye la consulta externa, no la lógica de pedidos ni de stock.
        with patch("pedidos.verificacion.consultar_orden", return_value=respuesta):
            for intento in (1, 2):
                with self.subTest(verificacion=intento):
                    self.assertEqual(verificar_pago_de_compra(compra), "confirmada")
                    compra.refresh_from_db()
                    pedido.refresh_from_db()
                    variante.refresh_from_db()
                    self.assertEqual(compra.estado, Compra.Estado.CONFIRMADA)
                    self.assertEqual(pedido.estado, Pedido.Estado.PREPARACION)
                    self.assertEqual(variante.stock, 4)
