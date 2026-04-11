# EnergyTrack

EnergyTrack is a Flask-based energy monitoring platform with:
- user authentication
- real-time usage dashboards
- billing estimation
- admin portal
- ML-based prediction features

This README is intentionally short and product-focused.

## 1. Tech Stack

- Python 3.10+
- Flask
- SQLite
- scikit-learn
- Bootstrap

## 2. Quick Start (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python generate_dataset.py
python -c "from ml.predictor import train_model_script; train_model_script()"
python app.py
```

Open: http://127.0.0.1:5000

Admin portal (separate app):

```powershell
python admin_app.py
```

Open: http://127.0.0.1:5001

## 3. Required Environment Setup

Edit `.env` before production deployment:

```env
SECRET_KEY=replace-with-a-long-random-secret
FLASK_ENV=production
FLASK_DEBUG=False

ADMIN_EMAIL=admin@energytrack.local
ADMIN_PASSWORD=replace-with-strong-password
```

Notes:
- Admin account is created only when both `ADMIN_EMAIL` and `ADMIN_PASSWORD` are configured.
- Never commit `.env`.

## 4. Product-Readiness Checklist

- Set strong `SECRET_KEY` and admin password
- Keep `FLASK_DEBUG=False` in production
- Use a managed database for production
- Set up HTTPS and reverse proxy (Nginx/Caddy)
- Configure email provider credentials if OTP email is required
- Add monitoring/logging for runtime errors

## 5. Common Commands

```powershell
# install dependencies
pip install -r requirements.txt

# run user app
python app.py

# run admin app
python admin_app.py

# setup helper
python setup.py

# smart launcher with pre-checks
python run.py
```

## 6. Repository Hygiene

Already protected in `.gitignore`:
- `.env`
- databases
- model artifacts
- caches

If you accidentally commit secrets, rotate them immediately.

## 7. GitHub Workflow

Follow the beginner guide in `GITHUB_DAILY_WORKFLOW.md`.

It includes:
- first push
- daily update steps
- branch and PR flow
- commit message format

## 8. Project Standards

- Contribution process: `CONTRIBUTING.md`
- Security reporting policy: `SECURITY.md`

## 9. Collaboration and CI

- Issue templates and PR template are configured in `.github/`
- Basic CI runs on push/PR to `main` via `.github/workflows/ci.yml`

## 10. Release Notes

- Current draft release notes: `RELEASE_NOTES_v1.0.0.md`

## 11. License

This project is licensed under the MIT License. See `LICENSE`.
