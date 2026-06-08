# Deploying Fabricator on Ubuntu VPS (Hostinger)

Production stack: **PostgreSQL + Gunicorn + Nginx**, managed by **Docker Compose** with auto-restart.

```
Internet → Nginx (port 80/443) → /api/* → Gunicorn (Flask)
                               → /*     → React static files
                                        ↘ PostgreSQL (persistent volume)
```

---

## Prerequisites

- Ubuntu 22.04 or 24.04 VPS (Hostinger KVM)
- Domain pointed to VPS IP (A record) — required for HTTPS
- SSH access as root or sudo user

---

## First-time setup (≈10 minutes)

### 1. Connect to your VPS

```bash
ssh root@YOUR_VPS_IP
```

### 2. Bootstrap Docker + firewall

```bash
git clone <your-repo-url> /opt/fabricator
cd /opt/fabricator/Fabricator   # adjust path if needed
chmod +x scripts/*.sh
sudo bash scripts/setup-vps.sh
```

### 3. Configure environment

```bash
bash scripts/deploy.sh          # creates .env with generated secrets
nano .env                       # edit required values
```

| Variable | Example |
|----------|---------|
| `DOMAIN` | `fabricator.yourdomain.com` |
| `CORS_ORIGINS` | `https://fabricator.yourdomain.com` |
| `TRAINER_EMAIL` | `trainer@yourdomain.com` |
| `TRAINER_PASSWORD` | strong password (min 12 chars) |
| `SEED_DEMO_DATA` | `false` for production |

### 4. Deploy

```bash
bash scripts/deploy.sh
```

Open `http://YOUR_VPS_IP` — you should see the login page.

Login with the **trainer email/password** from `.env`.

### 5. Enable HTTPS (recommended)

After DNS propagates (domain → VPS IP):

```bash
bash scripts/enable-ssl.sh
```

Visit `https://yourdomain.com`.

---

## Day-2 operations

| Task | Command |
|------|---------|
| View logs | `docker compose logs -f` |
| Restart API | `docker compose restart backend` |
| Update app | `git pull && bash scripts/deploy.sh` |
| Stop everything | `docker compose down` |
| Backup database | `docker compose exec db pg_dump -U fabricator fabricator > backup.sql` |

### Auto-restart

All services use `restart: unless-stopped` — they come back after VPS reboot automatically.

### SSL renewal

Add a monthly cron job on the VPS:

```bash
crontab -e
```

```
0 3 1 * * cd /opt/fabricator/Fabricator && docker compose -f docker-compose.yml -f docker-compose.ssl.yml exec -T web certbot renew && docker compose restart web
```

Or re-run `bash scripts/enable-ssl.sh` before expiry (every 90 days).

---

## Local development (unchanged)

```bash
# Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade && python seed.py
python run.py

# Frontend
cd frontend && npm install && npm run dev
```

Set `SEED_DEMO_DATA=true` in `backend/.env` for demo students.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `502 Bad Gateway` on `/api` | `docker compose logs backend` — check DB connection |
| Login fails after deploy | Confirm `flask db upgrade` ran: `docker compose logs backend` |
| Port 80 in use | `sudo lsof -i :80` — stop conflicting service |
| CORS errors | Set `CORS_ORIGINS` to your exact frontend URL in `.env`, restart backend |

---

## Security checklist

- [x] PostgreSQL not exposed publicly (internal Docker network only)
- [x] Gunicorn not exposed publicly (only Nginx is public)
- [x] Strong secrets auto-generated
- [x] Demo data disabled by default (`SEED_DEMO_DATA=false`)
- [x] Production config validates secrets on startup
- [ ] HTTPS enabled (`enable-ssl.sh`)
- [ ] Firewall allows only 22, 80, 443

---

## Resource requirements

| Students | Minimum VPS |
|----------|-------------|
| ~60 | 2 GB RAM, 1 vCPU |
| 100+ | 4 GB RAM, 2 vCPU |

Set `GUNICORN_WORKERS=2` on small VPS in `.env`.
