from django.contrib import admin

from portfolio.models import PhishingReport


@admin.register(PhishingReport)
class PhishingReportAdmin(admin.ModelAdmin):
    list_display = ("organization", "report_type", "incident_date", "status", "created_at")
    list_filter = ("status", "report_type", "created_at")
    search_fields = ("organization", "indicator", "zambia_connection", "details")
    readonly_fields = ("created_at",)
    ordering = ("status", "-created_at")
