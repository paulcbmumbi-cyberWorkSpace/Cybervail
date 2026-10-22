from django.db import models


class PhishingReport(models.Model):
    class ReportType(models.TextChoices):
        EMAIL = "email", "Phishing email"
        WEBSITE = "website", "Phishing website"
        SMS = "sms", "SMS or messaging scam"
        SOCIAL = "social", "Social media scam"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"

    organization = models.CharField(max_length=120)
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
        default=ReportType.EMAIL,
    )
    incident_date = models.DateField(null=True, blank=True)
    indicator = models.CharField(max_length=2048)
    zambia_connection = models.CharField(max_length=300, blank=True)
    details = models.CharField(max_length=1000)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "phishing report"
        verbose_name_plural = "phishing reports"

    def __str__(self):
        return f"{self.organization} — {self.get_report_type_display()}"

    @property
    def defanged_indicator(self):
        value = self.indicator.replace("https://", "hxxps://").replace("http://", "hxxp://")
        return value.replace(".", "[.]")
