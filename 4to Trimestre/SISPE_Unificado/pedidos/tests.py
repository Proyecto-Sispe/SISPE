from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from . import views


class SeleccionMetodoPagoTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.factura = SimpleNamespace(
            estado="emitida",
            metodo_pago="",
            transaccion_id="",
            subtotal=Decimal("0"),
            impuesto=Decimal("0"),
            propina=Decimal("0"),
            total=Decimal("0"),
            save=Mock(),
        )
        self.pedido = SimpleNamespace(
            pk=12,
            id_pedido=12,
            id_mesa=3,
            total=Decimal("10000"),
            estado="pendiente",
            factura=self.factura,
        )

    def test_selecting_cash_saves_pending_method_for_cashier(self):
        request = self.factory.post(
            reverse("factura_cliente", args=[self.pedido.pk]),
            {"metodo_pago": "efectivo"},
        )
        request.session = {}

        with (
            patch("pedidos.views.get_object_or_404", return_value=self.pedido),
            patch("pedidos.views.messages"),
        ):
            response = views.factura_cliente(request, self.pedido.pk)

        self.assertRedirects(
            response, reverse("factura_cliente", args=[self.pedido.pk]), fetch_redirect_response=False
        )
        self.assertEqual(self.factura.metodo_pago, "Efectivo - Pendiente en caja")
        self.factura.save.assert_called_once_with(
            update_fields=["metodo_pago", "transaccion_id"]
        )

    def test_pse_screen_requires_pse_selection(self):
        self.factura.metodo_pago = views.METODOS_PAGO_PENDIENTES["pse"]
        request = self.factory.get(reverse("factura_cliente", args=[self.pedido.pk]))
        request.session = {}
        rendered = HttpResponse()

        with (
            patch("pedidos.views.get_object_or_404", return_value=self.pedido),
            patch("pedidos.views.render", return_value=rendered) as render,
        ):
            response = views.factura_cliente(request, self.pedido.pk)

        self.assertIs(response, rendered)
        self.assertEqual(render.call_args.args[2]["metodo_seleccionado"], "pse")

    def test_pse_endpoint_rejects_invoice_without_pse_selection(self):
        self.factura.metodo_pago = views.METODOS_PAGO_PENDIENTES["efectivo"]
        request = self.factory.post(
            reverse("pagar_pse", args=[self.pedido.pk]),
            {"banco": "bancolombia"},
        )
        request.session = {}

        with (
            patch("pedidos.views.get_object_or_404", return_value=self.pedido),
            patch("pedidos.views.messages"),
        ):
            response = views.pagar_pse(request, self.pedido.pk)

        self.assertRedirects(
            response, reverse("factura_cliente", args=[self.pedido.pk]), fetch_redirect_response=False
        )
        self.factura.save.assert_not_called()
        self.assertEqual(self.factura.estado, "emitida")
