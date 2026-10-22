from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from portfolio.forms import PhishingReportForm
from portfolio.models import PhishingReport
from portfolio.phishing_feed import get_zambia_phishing_feed


def home(request):
    if request.method == "POST":
        form = PhishingReportForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thank you. Your report is saved privately and will be reviewed before publication.",
            )
            return redirect(f"{reverse('home')}#report-phishing")
    else:
        form = PhishingReportForm()

    reports = PhishingReport.objects.filter(status=PhishingReport.Status.PUBLISHED)
    search_query = request.GET.get("q", "").strip()[:100]
    if search_query:
        reports = reports.filter(
            Q(organization__icontains=search_query)
            | Q(indicator__icontains=search_query)
            | Q(details__icontains=search_query)
        )

    page = Paginator(reports, 10).get_page(request.GET.get("page"))
    return render(
        request,
        "portfolio/index.html",
        {
            "report_form": form,
            "archive_page": page,
            "search_query": search_query,
        },
    )


def zambia_phishing_feed(request):
    return JsonResponse(get_zambia_phishing_feed())
