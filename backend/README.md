# Fabricator Backend

Flask REST API for the Workshop Performance Tracking System.

## Local development

```bash
cd Fabricator/backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env
```

```bash
set FLASK_APP=manage.py
flask db upgrade
python seed.py
python run.py
```

API: `http://localhost:5000/api/v1`

## Production (Ubuntu VPS)

See **[../DEPLOY.md](../DEPLOY.md)** for Docker Compose deployment on Hostinger VPS.

Quick start on server:

```bash
bash scripts/setup-vps.sh
bash scripts/deploy.sh
```

## Default credentials (development only)

| Role    | Email                   | Password    |
|---------|-------------------------|-------------|
| Trainer | trainer@workshop.local  | trainer123  |
| Student | alice@demo.local        | student123  |

Set `SEED_DEMO_DATA=true` in `.env` to create demo students locally.

## Environment

| Variable         | Description                          |
|------------------|--------------------------------------|
| DATABASE_URL     | SQLite (dev) or PostgreSQL (prod)    |
| JWT_SECRET_KEY   | JWT signing secret                   |
| SECRET_KEY       | Flask secret key                     |
| TRAINER_EMAIL    | Initial trainer account              |
| TRAINER_PASSWORD | Initial trainer password             |
| SEED_DEMO_DATA   | `true` to seed demo workshop data    |
| CORS_ORIGINS     | Comma-separated allowed origins      |

