from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


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
