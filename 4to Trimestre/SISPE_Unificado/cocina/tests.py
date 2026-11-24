from datetime import datetime
from decimal import Decimal
from io import BytesIO
from types import SimpleNamespace

from django.test import SimpleTestCase
from openpyxl import load_workbook

from .reportes import exportar_excel, exportar_pdf


class ReportesExportTests(SimpleTestCase):
    def setUp(self):
        pedido = SimpleNamespace(
            fecha_pedido=datetime(2026, 11, 24, 12, 30),
            id_mesa=3,
            get_estado_display=lambda: "Entregado",
        )
        detalle = SimpleNamespace(
            pedido_id=17,
            pedido=pedido,
            combo_id=None,
            descripcion="Arepa",
            cantidad=2,
            precio_unitario=Decimal("6000"),
            valor_venta=Decimal("12000"),
        )
        self.contexto = {
            "desde": "2026-11-01",
            "hasta": "2026-11-30",
            "categoria_nombre": "Comidas",
            "estado_nombre": "Entregado",
            "ventas": Decimal("12000"),
            "cantidad_pedidos": 1,
            "pedidos_entregados": 1,
            "mesas_ocupadas": 2,
            "ticket": Decimal("12000"),
            "producto_mas_vendido": "Arepa",
            "por_categoria": [
                {
                    "producto__categoria__nom_categoria": "Comidas",
                    "unidades": 2,
                    "total": Decimal("12000"),
                }
            ],
            "top": [
                {
                    "producto__nombre": "Arepa",
                    "unidades": 2,
                    "total": Decimal("12000"),
                }
            ],
            "combos_vendidos": [],
            "por_estado": [{"estado": "entregado", "n": 1}],
            "detalle_export": SimpleNamespace(iterator=lambda: iter([detalle])),
        }

    def test_excel_includes_filtered_summary_and_detail(self):
        response = exportar_excel(self.contexto)
        workbook = load_workbook(BytesIO(response.content), read_only=True)

        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("Resumen", workbook.sheetnames)
        self.assertIn("Detalle", workbook.sheetnames)
        detalle = workbook["Detalle"]
        self.assertEqual(detalle["F2"].value, "Arepa")
        self.assertEqual(detalle["I2"].value, Decimal("12000"))

    def test_pdf_is_returned_as_a_download(self):
        response = exportar_pdf(self.contexto)

        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn('filename="reporte_sispe.pdf"', response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF-"))
