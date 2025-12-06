# Deployment Guide

This project ships with a production-ready Docker image that can be run on free container hosts such as Render, Railway, Fly.io, or Google Cloud Run. Below is a tested Render setup that exposes your APIs over HTTPS for the Flutter client.

## 1. Configure Environment Variables
Copy `.env.example` to `.env` locally and fill in the following values:

```
cp .env.example .env
```

| Variable | Description |
| --- | --- |
| `DJANGO_SECRET_KEY` | Strong random string |
| `DJANGO_DEBUG` | `0` for production, `1` for local dev |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated domains (e.g. `your-service.onrender.com`) |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated origins with scheme (e.g. `https://your-service.onrender.com`) |
| `DATABASE_URL` | `postgresql://USER:PASSWORD@HOST:PORT/DBNAME` |
| `EMAIL_HOST_USER` | Gmail address for sending emails (e.g. `yourapp@gmail.com`) |
| `EMAIL_HOST_PASSWORD` | Gmail App Password (16-character, NOT your regular password) |

`docker-compose.yml` uses these values automatically for local development. In production, add the same variables through the provider's dashboard.

## 2. Push the Code to GitHub
Render pulls code from Git providers.

```
git add .
git commit -m "Prepare deployment"
git push origin main
```

## 3. Create Resources on Render
1. Create a **PostgreSQL** instance (`New -> PostgreSQL`). Copy the generated `DATABASE_URL`.
2. Create a **Web Service** (`New -> Web Service`) and select your GitHub repo. Render detects the `Dockerfile` automatically.

## 4. Configure the Web Service
- **Start Command:** `gunicorn API.wsgi:application --bind 0.0.0.0:8000`
- **Environment Variables:**
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG=0`
  - `DJANGO_ALLOWED_HOSTS=your-service.onrender.com`
  - `DJANGO_CSRF_TRUSTED_ORIGINS=https://your-service.onrender.com`
  - `DATABASE_URL=<value from PostgreSQL instance>`
  - `EMAIL_HOST_USER=<your Gmail address>`
  - `EMAIL_HOST_PASSWORD=<Gmail App Password>`
  - Any third-party API keys in use (Stripe, Google, etc.)

**Note:** To get a Gmail App Password:
1. Enable 2-Factor Authentication on your Google Account
2. Go to Google Account → Security → 2-Step Verification → App Passwords
3. Generate a new app password for "Mail"
4. Use the generated 16-character password (not your regular Gmail password)

## 5. Run One-off Tasks
From the service page, open the **Shell** and execute:

```
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # optional
```

## 6. Deploy & Verify
Click **Deploy latest commit**. When the status changes to *Live*, Render provides an HTTPS URL. Test endpoints via curl/Postman and share the base URL with the Flutter teammate.

## 7. Optional Improvements
- Add `render.yaml` for infra-as-code
- Attach a custom domain (Render handles TLS)
- Set up cron/worker services if background jobs are needed

For Railway, Fly.io, or Cloud Run, reuse the same Docker image and environment variables—the only changes are platform-specific commands and database wiring.
