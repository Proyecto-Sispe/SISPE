from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from cocina.views import qr_mesas
from menu.views import qr_imagen, qr_mesa
from mesas_pedidos.views import mesas_list


class QrRoleAccessTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def request_for_role(self, role):
        request = self.factory.get("/servicio/mesas/")
        request.user = SimpleNamespace(is_authenticated=True, is_superuser=False)
        request.session = {"usuario_rol": role}
        return request

    @patch("mesas_pedidos.views._ips_locales", return_value=[])
    @patch("mesas_pedidos.views._mesas_con_qr", return_value=[])
    @patch("mesas_pedidos.views.render", return_value=HttpResponse())
    def test_mesero_can_manage_tables_without_qr_controls(self, render, build_mesas, _ips):
        response = mesas_list(self.request_for_role("mesero"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(render.call_args.args[2]["puede_gestionar_qr"])
        build_mesas.assert_called_once_with("testserver", False)

    def test_qr_pages_require_administrator_role(self):
        request = self.request_for_role("cocinero")
        denied = HttpResponse(status=403)

        with patch("administracion.permisos.render", return_value=denied):
            self.assertEqual(qr_mesas(request).status_code, 403)
            self.assertEqual(qr_mesa(request, 1).status_code, 403)
            self.assertEqual(qr_imagen(request, 1).status_code, 403)
