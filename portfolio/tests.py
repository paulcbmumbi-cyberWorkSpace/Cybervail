from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_homepage_renders_portfolio_and_static_assets(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Paul Chola Bwembya Mumbi")
        self.assertContains(response, "/static/portfolio/style.css")
        self.assertContains(response, "/static/portfolio/script.js")
