# Django Portfolio

A Django-powered version of the cybersecurity portfolio website.

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
- `portfolio/` contains the homepage view and tests.
- `templates/portfolio/` contains the website template.
- `static/portfolio/` contains CSS, JavaScript, images, and downloadable documents.

Edit `templates/portfolio/index.html` for page content and `static/portfolio/` for styles, behavior, and media.

## Tests

```powershell
python manage.py test
```

## GitHub and deployment

This is a standalone project folder. To publish it as a new GitHub repository, create an empty repository on GitHub, then run these commands from this folder, replacing the URL with your new repository URL:

```powershell
git init
git add .
git commit -m "Create Django portfolio"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

GitHub stores the source code but does not host Django applications. Deploy the project to a Django-compatible hosting provider to make the site publicly available. Configure a production `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and static-file serving there; do not use the local development secret key in production.
