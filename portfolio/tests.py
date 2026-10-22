from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from portfolio.models import PhishingReport


class HomePageTests(TestCase):
    def test_homepage_renders_cyber_safety_guidance_and_static_assets(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Paul Chola Bwembya Mumbi")
        self.assertContains(response, "Cybersecurity")
        self.assertContains(response, "for everyday life.")
        self.assertContains(response, "What is phishing?")
        self.assertContains(response, "Zambia phishing watch")
        self.assertContains(response, "does not confirm who a site targets")
        self.assertContains(response, "Suspected Barrick Lumwana recruitment impersonation")
        self.assertContains(response, "Barrick is an international mining company with operations in Zambia, including Lumwana")
        self.assertContains(response, "ul-rec[.]github[.]io/lumwana")
        self.assertContains(response, "Phishing email report · Zambia")
        self.assertContains(response, "Link in reported email")
        self.assertContains(response, "claim has not been independently verified")
        self.assertNotContains(response, "https://ul-rec.github.io/lumwana")
        self.assertContains(response, "Suspected Electoral Commission of Zambia recruitment phishing")
        self.assertContains(response, "ecz-career[.]alloffer[.]org")
        self.assertContains(response, "GitHub confirmed policy action")
        self.assertContains(response, "GitHub did not specify the action")
        self.assertNotContains(response, "http://ecz-career.alloffer.org")
        self.assertContains(response, "/static/portfolio/style.css")
        self.assertContains(response, "/static/portfolio/script.js")
        self.assertContains(response, "Report a suspicious message or link")
        self.assertContains(response, "Zambia phishing archive")
        self.assertContains(response, "Reports are private until reviewed")

    def test_report_submission_is_private_until_approved(self):
        response = self.client.post(
            reverse("home"),
            {
                "organization": "Example Bank Zambia",
                "report_type": PhishingReport.ReportType.EMAIL,
                "incident_date": "2026-10-19",
                "indicator": "https://login.example.com/verify",
                "zambia_connection": "The email targets a recruitment programme in Zambia.",
                "details": "Unexpected message requested account verification.",
                "confirm_safe_to_share": "on",
            },
        )

        self.assertRedirects(response, f"{reverse('home')}#report-phishing")
        report = PhishingReport.objects.get()
        self.assertEqual(report.status, PhishingReport.Status.PENDING)

        page = self.client.get(reverse("home"))
        self.assertNotContains(page, "login[.]example[.]com")

    def test_published_archive_search_defangs_reported_indicator(self):
        PhishingReport.objects.create(
            organization="Example Bank Zambia",
            report_type=PhishingReport.ReportType.EMAIL,
            indicator="https://login.example.com/verify",
            zambia_connection="The email targets a recruitment programme in Zambia.",
            details="Unexpected message requested account verification.",
            status=PhishingReport.Status.PUBLISHED,
        )

        response = self.client.get(reverse("home"), {"q": "Example Bank"})

        self.assertContains(response, "Example Bank Zambia impersonation report")
        self.assertContains(response, "hxxps://login[.]example[.]com/verify")
        self.assertNotContains(response, "https://login.example.com/verify")

    def test_report_form_rejects_script_urls(self):
        response = self.client.post(
            reverse("home"),
            {
                "organization": "Example Bank Zambia",
                "report_type": PhishingReport.ReportType.EMAIL,
                "indicator": "javascript:alert(1)",
                "zambia_connection": "It claims to be about a Zambian service.",
                "details": "Suspicious message.",
                "confirm_safe_to_share": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PhishingReport.objects.count(), 0)
        self.assertContains(response, "Enter a domain or an http/https link")

    @patch(
        "portfolio.views.get_zambia_phishing_feed",
        return_value={
            "status": "live",
            "checked_at": "2026-10-20T15:00:00+00:00",
            "source": "OpenPhish community feed",
            "source_url": "https://openphish.com/",
            "feed_entries_scanned": 10,
            "match_count": 1,
            "entries": [{"domain": "login[.]example[.]zm", "indicator": ".zm domain"}],
            "error": "",
        },
    )
    def test_phishing_feed_endpoint_returns_zambia_indicators(self, get_feed):
        response = self.client.get(reverse("zambia-phishing-feed"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["match_count"], 1)
        self.assertEqual(response.json()["entries"][0]["domain"], "login[.]example[.]zm")

    def test_zambia_indicators_are_limited_to_configured_hostnames(self):
        from portfolio.phishing_feed import _zambia_indicator

        self.assertEqual(_zambia_indicator("login.example.zm"), ".zm domain")
        self.assertEqual(_zambia_indicator("zanaco-login.example.com"), "Zanaco keyword")
        self.assertIsNone(_zambia_indicator("unrelated.example.com"))

    @patch("portfolio.phishing_feed.urlopen")
    def test_feed_returns_only_defanged_zambia_indicator_domains(self, open_url):
        from portfolio.phishing_feed import _fetch_feed

        response = open_url.return_value.__enter__.return_value
        response.read.return_value = (
            b"https://login.example.zm/path\n"
            b"https://zanaco-login.example.com/sign-in\n"
            b"https://unrelated.example.com/\n"
        )

        data = _fetch_feed()

        self.assertEqual(data["match_count"], 2)
        self.assertEqual(
            [entry["domain"] for entry in data["entries"]],
            ["login[.]example[.]zm", "zanaco-login[.]example[.]com"],
        )
        self.assertNotIn("https://", str(data["entries"]))
