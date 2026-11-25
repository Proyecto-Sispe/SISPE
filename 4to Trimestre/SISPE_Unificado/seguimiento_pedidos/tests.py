import hashlib
import re
from datetime import timedelta
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core import mail
from django.db import connections
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from administracion.models import LoginThrottle

from .models import PasswordResets, Persona, PersonaHasRol, Rol, TipoDoc


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="no-reply@sispe.test",
)
class PasswordResetTests(TestCase):
    databases = {"default"}

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="reset-user",
            email="reset-user@sispe.test",
            password="Original-password-123",
        )

    def test_password_reset_updates_password_through_email_link(self):
        response = self.client.post(
            reverse("password_reset"),
            {"email": self.user.email},
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])

        reset_url = next(
            line.strip()
            for line in mail.outbox[0].body.splitlines()
            if "/reset/" in line
        )
        response = self.client.get(reset_url, follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            response.wsgi_request.path,
            {
                "new_password1": "Updated-password-456",
                "new_password2": "Updated-password-456",
            },
        )

        self.assertRedirects(response, reverse("password_reset_complete"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Updated-password-456"))

    def test_password_reset_pages_render(self):
        for route_name in ("password_reset", "password_reset_done"):
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="no-reply@sispe.test",
)
class PersonaPasswordFlowTests(TestCase):
    databases = {"default", "sistema"}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connections["sistema"].cursor() as cursor:
            cursor.execute(
                "CREATE TABLE tipo_doc (id_doc INTEGER PRIMARY KEY, tipo_doc VARCHAR(45), estado INTEGER)"
            )
            cursor.execute(
                'CREATE TABLE rol ("idRol" INTEGER PRIMARY KEY, "Nom_rol" VARCHAR(45))'
            )
            cursor.execute(
                'CREATE TABLE persona (id_usuario INTEGER, "pkfk_Tipo_doc" INTEGER, '
                '"Nom1_usu" VARCHAR(20), "Nom2_usu" VARCHAR(20), "Ape1_usu" VARCHAR(20), '
                '"Ape2_usu" VARCHAR(20), "Telefono" BIGINT, "Correo_usu" VARCHAR(45), '
                '"Password" VARCHAR(255), estado INTEGER, '
                'PRIMARY KEY (id_usuario, "pkfk_Tipo_doc"), '
                'FOREIGN KEY ("pkfk_Tipo_doc") REFERENCES tipo_doc(id_doc))'
            )
            cursor.execute(
                'CREATE TABLE persona_has_rol (pkfk_id_usuario INTEGER, "pkfk_Tipo_doc" INTEGER, '
                '"pkfk_idRol" INTEGER, PRIMARY KEY (pkfk_id_usuario, "pkfk_Tipo_doc", "pkfk_idRol"), '
                'FOREIGN KEY ("pkfk_idRol") REFERENCES rol("idRol"))'
            )
            cursor.execute(
                "CREATE TABLE password_resets ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "correo VARCHAR(120) NOT NULL, token VARCHAR(64) NOT NULL, "
                "codigo VARCHAR(6) NOT NULL, expira DATETIME NOT NULL, "
                "usado INTEGER NOT NULL, created_at DATETIME NOT NULL)"
            )
        from actualizar_bd import asegurar_columnas_recuperacion

        asegurar_columnas_recuperacion()

    def setUp(self):
        mail.outbox.clear()
        self.tipo_doc = TipoDoc.objects.using("sistema").create(
            id_doc=1, tipo_doc="Cédula", estado=1
        )
        self.rol = Rol.objects.using("sistema").create(
            idrol=1, nom_rol="Cliente"
        )

    def test_schema_update_adds_only_missing_recovery_fields(self):
        with connections["sistema"].cursor() as cursor:
            columns = {
                column.name.lower()
                for column in connections["sistema"].introspection.get_table_description(
                    cursor, "password_resets"
                )
            }
        self.assertTrue({"codigo_hash", "intentos"}.issubset(columns))

    def crear_persona(self, correo="persona@sispe.test", password="Old-secure-123!"):
        persona = Persona.objects.using("sistema").create(
            id_usuario=123456,
            pkfk_tipo_doc_id=self.tipo_doc.pk,
            nom1_usu="Prueba",
            ape1_usu="Usuario",
            telefono=3001234567,
            correo_usu=correo,
            password=password,
            estado=1,
        )
        PersonaHasRol.objects.using("sistema").create(
            pkfk_id_usuario=persona.id_usuario,
            pkfk_tipo_doc=self.tipo_doc.pk,
            pkfk_idrol_id=self.rol.pk,
        )
        return persona

    def pedir_recuperacion(self, correo="persona@sispe.test"):
        response = self.client.post(
            reverse("api_recuperar_password"),
            data='{"correo": "%s"}' % correo,
            content_type="application/json",
        )
        return response

    def datos_correo(self):
        body = mail.outbox[-1].body
        codigo = re.search(r"Código de verificación: ([0-9]{6})", body).group(1)
        link = next(line.split(": ", 1)[1] for line in body.splitlines() if "Enlace de recuperación:" in line)
        self.assertEqual(urlsplit(link).query, "")
        token = parse_qs(urlsplit(link).fragment)["token"][0]
        return codigo, token

    def completar_recuperacion(self, token, codigo, password):
        return self.client.post(
            reverse("recuperar_password"),
            {
                "token": token,
                "codigo": codigo,
                "password": password,
                "confirmacion": password,
            },
        )

    def test_registration_login_and_legacy_password_upgrade(self):
        response = self.client.post(
            reverse("registro"),
            {
                "doc": str(self.tipo_doc.pk),
                "id": "456789",
                "nombre1": "Nuevo",
                "apellido1": "Cliente",
                "email": "nuevo@sispe.test",
                "telefono": "3001234567",
                "password": "Registered-Secure-985!",
            },
        )
        self.assertRedirects(response, reverse("login"))
        registered = Persona.objects.using("sistema").get(correo_usu="nuevo@sispe.test")
        self.assertNotEqual(registered.password, "Registered-Secure-985!")
        self.assertTrue(
            self.client.post(
                reverse("login"),
                {"correo": registered.correo_usu, "password": "wrong-password"},
            ).status_code
            == 200
        )
        response = self.client.post(
            reverse("login"),
            {"correo": registered.correo_usu, "password": "Registered-Secure-985!"},
        )
        self.assertRedirects(response, reverse("dashboard_cliente"))
        response = self.client.post(
            reverse("cambiar_password"),
            {
                "old_password": "Registered-Secure-985!",
                "new_password1": "Changed-Secure-481!",
                "new_password2": "Changed-Secure-481!",
            },
        )
        self.assertRedirects(response, reverse("portal"))
        registered.refresh_from_db(using="sistema")
        self.assertTrue(check_password("Changed-Secure-481!", registered.password))
        response = self.client.post(
            reverse("login"),
            {"correo": registered.correo_usu, "password": "Registered-Secure-985!"},
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse("login"),
            {"correo": registered.correo_usu, "password": "Changed-Secure-481!"},
        )
        self.assertRedirects(response, reverse("dashboard_cliente"))

        legacy = self.crear_persona(
            correo="legacy@sispe.test",
            password="Legacy-Plain-98!",
        )
        response = self.client.post(
            reverse("login"),
            {"correo": legacy.correo_usu, "password": "Legacy-Plain-98!"},
        )
        self.assertRedirects(response, reverse("dashboard_cliente"))
        legacy.refresh_from_db(using="sistema")
        self.assertTrue(legacy.password.startswith("pbkdf2_sha256$"))

    def test_registration_rejects_a_weak_password(self):
        response = self.client.post(
            reverse("registro"),
            {
                "doc": str(self.tipo_doc.pk),
                "id": "456790",
                "nombre1": "Nuevo",
                "apellido1": "Cliente",
                "email": "weak@sispe.test",
                "telefono": "3001234567",
                "password": "123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Persona.objects.using("sistema").filter(
                correo_usu="weak@sispe.test"
            ).exists()
        )

    def test_login_is_rate_limited_after_repeated_failures(self):
        persona = self.crear_persona()
        for _ in range(8):
            response = self.client.post(
                reverse("login"),
                {"correo": persona.correo_usu, "password": "Wrong-password"},
            )
            self.assertEqual(response.status_code, 200)

        self.assertEqual(LoginThrottle.objects.using("default").count(), 2)
        response = self.client.post(
            reverse("login"),
            {"correo": persona.correo_usu, "password": "Old-secure-123!"},
        )
        self.assertEqual(response.status_code, 200)

    def test_reset_hashes_code_and_token_and_invalidates_them_after_use(self):
        persona = self.crear_persona()
        desconocido = self.pedir_recuperacion("not-registered@sispe.test")
        conocido = self.pedir_recuperacion()
        self.assertEqual(desconocido.status_code, conocido.status_code)
        self.assertEqual(desconocido.json(), conocido.json())
        self.assertEqual(len(mail.outbox), 1)
        reset = PasswordResets.objects.using("sistema").get()
        codigo, token = self.datos_correo()
        cuerpo_html = mail.outbox[0].alternatives[0][0]
        self.assertIn(codigo, cuerpo_html)
        self.assertIn(token, cuerpo_html)
        self.assertIn("15 minutos", cuerpo_html)
        self.assertEqual(reset.codigo, "")
        self.assertNotEqual(reset.token, token)
        self.assertTrue(reset.token == hashlib.sha256(token.encode()).hexdigest())
        self.assertTrue(check_password(codigo, reset.codigo_hash))

        wrong_code = "000000" if codigo != "000000" else "000001"
        response = self.completar_recuperacion(
            token, wrong_code, "New-Strong-Pass-125!"
        )
        self.assertRedirects(
            response,
            reverse("recuperar_password") + "#token=" + token,
            fetch_redirect_response=False,
        )
        reset.refresh_from_db(using="sistema")
        self.assertEqual(reset.intentos, 1)

        nueva = "New-Strong-Pass-125!"
        response = self.completar_recuperacion(token, codigo, nueva)
        self.assertRedirects(response, reverse("login"))
        persona.refresh_from_db(using="sistema")
        self.assertTrue(check_password(nueva, persona.password))
        reset.refresh_from_db(using="sistema")
        self.assertEqual(reset.usado, 1)

        response = self.completar_recuperacion(token, codigo, "Another-Strong-336!")
        self.assertRedirects(response, reverse("recuperar_password"))
        response = self.client.post(
            reverse("login"),
            {"correo": persona.correo_usu, "password": "Old-secure-123!"},
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse("login"),
            {"correo": persona.correo_usu, "password": nueva},
        )
        self.assertRedirects(response, reverse("dashboard_cliente"))

    def test_reset_locks_after_five_wrong_code_attempts(self):
        self.crear_persona()
        self.pedir_recuperacion()
        codigo, token = self.datos_correo()
        reset = PasswordResets.objects.using("sistema").get()

        wrong_code = "000000" if codigo != "000000" else "000001"
        for _ in range(5):
            self.completar_recuperacion(
                token, wrong_code, "New-Strong-Pass-125!"
            )
        reset.refresh_from_db(using="sistema")
        self.assertEqual(reset.usado, 1)
        response = self.completar_recuperacion(
            token, codigo, "New-Strong-Pass-125!"
        )
        self.assertRedirects(response, reverse("recuperar_password"))

    def test_new_recovery_invalidates_previous_requests(self):
        self.crear_persona()
        self.pedir_recuperacion()
        previous = PasswordResets.objects.using("sistema").get()
        previous.created_at = timezone.now() - timedelta(minutes=2)
        previous.save(using="sistema", update_fields=["created_at"])

        self.pedir_recuperacion()
        previous.refresh_from_db(using="sistema")
        latest = PasswordResets.objects.using("sistema").order_by("-created_at").first()
        self.assertEqual(previous.usado, 1)
        self.assertNotEqual(previous.pk, latest.pk)

    def test_expired_reset_code_is_rejected(self):
        self.crear_persona()
        self.pedir_recuperacion()
        codigo, token = self.datos_correo()
        reset = PasswordResets.objects.using("sistema").get()
        reset.expira = timezone.now() - timedelta(seconds=1)
        reset.save(using="sistema", update_fields=["expira"])
        response = self.completar_recuperacion(
            token, codigo, "New-Strong-Pass-125!"
        )
        self.assertRedirects(response, reverse("recuperar_password"))
