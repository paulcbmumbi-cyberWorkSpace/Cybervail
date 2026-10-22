from urllib.parse import urlsplit

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from portfolio.models import PhishingReport


class PhishingReportForm(forms.ModelForm):
    zambia_connection = forms.CharField(
        label="Why might this be connected to Zambia?",
        max_length=300,
        required=True,
        help_text="For example, it impersonates a Zambian organisation or was received in Zambia.",
    )
    confirm_safe_to_share = forms.BooleanField(
        label="I have not included passwords, personal information, full email contents, or attachments.",
        required=True,
    )

    class Meta:
        model = PhishingReport
        fields = (
            "organization",
            "report_type",
            "incident_date",
            "indicator",
            "details",
        )
        labels = {
            "organization": "Organization being impersonated",
            "report_type": "What did you receive?",
            "incident_date": "When did you receive or find it? (optional)",
            "indicator": "Suspicious link or domain",
            "details": "What made it look suspicious?",
        }
        widgets = {
            "incident_date": forms.DateInput(attrs={"type": "date"}),
            "details": forms.Textarea(attrs={"rows": 4, "maxlength": 1000}),
        }

    def clean_indicator(self):
        indicator = self.cleaned_data["indicator"].strip()
        candidate = (
            indicator.replace("hxxps://", "https://")
            .replace("hxxp://", "http://")
            .replace("[.]", ".")
        )
        if "://" not in candidate:
            candidate = f"https://{candidate}"
        validator = URLValidator(schemes=("http", "https"))

        try:
            validator(candidate)
        except ValidationError as error:
            raise forms.ValidationError(
                "Enter a domain or an http/https link. Do not open the link to check it."
            ) from error

        parsed = urlsplit(candidate)
        if not parsed.hostname or parsed.username or parsed.password:
            raise forms.ValidationError("Enter a valid domain or link without login credentials.")
        return indicator
