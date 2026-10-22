# Cybervail

A Django-powered Zambia-focused cybersecurity awareness and phishing-reporting website.

## Run locally on Windows

Install Python 3.10 or newer, then open PowerShell in this folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser.

## Project layout

- `config/` contains Django settings and URL configuration.
- `portfolio/` contains the phishing feed, report model, moderation admin, views, and tests.
- `templates/portfolio/` contains the website template.
- `static/portfolio/` contains CSS, JavaScript, images, and downloadable documents.

Edit `templates/portfolio/index.html` for page content and `static/portfolio/` for styles, behavior, and media.

## Zambia phishing reports

The dashboard checks a public phishing feed and refreshes its displayed snapshot every 15 minutes. This is not an inbox scanner or a guarantee of real-time detection; upstream feed coverage and update times can vary.

Visitors can submit a suspicious domain or link with context. Submissions are private by default and appear in the public archive only after a reviewer publishes them through Django admin. The form does not accept full email contents or attachments and asks reporters not to submit passwords, one-time codes, or personal information. Indicators shown publicly are defanged and should not be visited.

Create an administrator account to review submissions:

```powershell
python manage.py createsuperuser
```

Sign in at <http://127.0.0.1:8000/admin/> and change a report's status to **Published** only after review. Publish does not necessarily mean every allegation has been independently verified; preserve that distinction in report details.

## Tests

```powershell
python manage.py test
```

## Deploy to Render

GitHub Pages cannot run this Django application. The included `render.yaml` configures a Django web service and PostgreSQL database on Render.

1. Push the project to GitHub. Review `git status` and the changes before committing; do not commit `.env`, database files, or secret keys.
2. In Render, create a new **Blueprint** and connect the `Cybervail` GitHub repository.
3. Review the web service and database resources from `render.yaml`, then apply the Blueprint. Render generates `DJANGO_SECRET_KEY` and runs migrations and static-file collection during the build.
4. Once the service is live, open its `onrender.com` URL and test the report form and phishing dashboard.
5. In the Render service shell, run `python manage.py createsuperuser` to create an account for reviewing reports at `/admin/`.

The included Blueprint uses Render's free plans for a demo. The web service can sleep when idle, and the free PostgreSQL database expires after 30 days; do not use this setup for real user reports or data that must be retained. Upgrade to paid plans and arrange backups before inviting people to submit reports. For a custom domain, add the domain to Render and update `DJANGO_ALLOWED_HOSTS` to include it.
