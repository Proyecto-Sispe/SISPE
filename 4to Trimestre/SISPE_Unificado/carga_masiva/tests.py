from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from menu.models import Categoria

from .models import HistorialCarga


class CargaMasivaImportTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(self.admin)

    def archivo(self):
        return SimpleUploadedFile("categorias.csv", b"nombre\nValida", content_type="text/csv")

    @patch("carga_masiva.views.leer_archivo", return_value=[{}, {}])
    @patch(
        "carga_masiva.views.validar_filas",
        return_value=(
            [{"nombre": "Categoría válida"}],
            [{"fila": 3, "error": "La categoría ya existe."}],
        ),
    )
    def test_importa_validos_aunque_haya_filas_con_errores(
        self, validar, leer
    ):
        manager = Mock()
        with patch.object(Categoria.objects, "using", return_value=manager):
            respuesta = self.client.post(
                reverse("carga_masiva_inicio"),
                {
                    "tipo": "categorias",
                    "archivo": self.archivo(),
                    "accion": "importar",
                },
            )

        self.assertRedirects(respuesta, reverse("carga_masiva_inicio"))
        manager.create.assert_called_once_with(nom_categoria="Categoría válida")
        carga = HistorialCarga.objects.get()
        self.assertEqual(carga.total_registros, 2)
        self.assertEqual(carga.registros_exitosos, 1)
        self.assertEqual(carga.registros_error, 1)
        self.assertEqual(carga.estado, "exitosa")

    @patch("carga_masiva.views.leer_archivo", return_value=[{}])
    @patch(
        "carga_masiva.views.validar_filas",
        return_value=([], [{"fila": 2, "error": "Falta el nombre."}]),
    )
    def test_no_intenta_importar_si_no_hay_filas_validas(self, validar, leer):
        manager = Mock()
        with patch.object(Categoria.objects, "using", return_value=manager):
            respuesta = self.client.post(
                reverse("carga_masiva_inicio"),
                {
                    "tipo": "categorias",
                    "archivo": self.archivo(),
                    "accion": "importar",
                },
            )

        self.assertEqual(respuesta.status_code, 200)
        manager.create.assert_not_called()
        carga = HistorialCarga.objects.get()
        self.assertEqual(carga.registros_exitosos, 0)
        self.assertEqual(carga.registros_error, 1)
        self.assertEqual(carga.estado, "fallida")
