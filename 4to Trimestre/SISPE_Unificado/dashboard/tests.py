
from django.test import SimpleTestCase
from django.urls import reverse


class LegacyStatisticsRedirectTests(SimpleTestCase):
    def test_statistics_url_redirects_to_integrated_reports(self):
        response = self.client.get(reverse("inicio"))

        self.assertRedirects(
            response,
            reverse("reportes"),
            fetch_redirect_response=False,
        )
