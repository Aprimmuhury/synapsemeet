# Deploying the SynapseMeet backend (Render.com)

Goal: get the Django API running on a public HTTPS URL, so the Android APK
(and anyone, anywhere) can reach it without being on your WiFi or emulator.

## 0. Prerequisites

- Push this whole `synapsemeet/` project to a GitHub repo (private is fine).
  Make sure `backend/venv/`, `backend/db.sqlite3`, `__pycache__/`, and
  `backend/.env` are in `.gitignore` — do not commit real secrets.
- A free Render.com account (sign in with GitHub).

## 1. Create the database

1. Render dashboard → **New +** → **PostgreSQL**.
2. Name: `synapsemeet-db`, region: closest to you, plan: Free.
3. After it's created, open it and copy these values (you'll need them in
   step 3): **Hostname**, **Port**, **Database**, **Username**, **Password**.
   Use the **Internal** hostname if your web service will be in the same
   Render region (faster, no extra cost).

## 2. Create the web service

1. Render dashboard → **New +** → **Web Service** → connect your GitHub repo.
2. **Root Directory:** `backend`
3. **Runtime:** Python 3
4. **Build Command:**
   ```
   pip install -r requirements.txt && python manage.py collectstatic --noinput
   ```
5. **Start Command:**
   ```
   gunicorn synapsemeet.wsgi --log-file -
   ```
   (Render reads the `Procfile` automatically too, so this is a backup —
   either works.)

## 3. Environment variables

In the web service's **Environment** tab, add:

| Key | Value |
| --- | --- |
| `SECRET_KEY` | generate one, e.g. run `python -c "import secrets; print(secrets.token_urlsafe(50))"` locally |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `synapsemeet.onrender.com` (use your actual Render URL once assigned — you can add it after the first deploy and redeploy) |
| `DB_ENGINE` | `postgres` |
| `DB_NAME` | from step 1 |
| `DB_USER` | from step 1 |
| `DB_PASSWORD` | from step 1 |
| `DB_HOST` | from step 1 |
| `DB_PORT` | `5432` |
| `DB_SSLMODE` | `require` |
| `FRONTEND_BASE_URL` | `https://synapsemeet.onrender.com` (same as your Render URL) |
| `AI_PROVIDER` | `anthropic` |
| `AI_API_KEY` | your real key, if you've wired one up |

Click **Create Web Service**. First deploy takes 5-10 minutes.

## 4. Run migrations

Render's free plan doesn't auto-run the `release:` line in `Procfile`. After
the first successful deploy, open the web service's **Shell** tab and run:
```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
```

## 5. Verify

Visit `https://<your-service>.onrender.com/` in a browser — you should see
the SynapseMeet login page (Django serves it via `frontend_views.py`).
Try registering an account to confirm the API + database work end to end.

## 6. Point the app at this URL

Edit `frontend/js/config.js`:
```js
window.SYNAPSEMEET_API_BASE = 'https://<your-service>.onrender.com/api';
```
Then re-sync the Android assets copy (see `../android/README.md`) before
building the APK.

## Notes

- **Free plan sleeps** after 15 min of inactivity; the first request after
  that can take 30-50 seconds to wake up. Normal — not a bug.
- **SQLite → Postgres**: your data does *not* carry over automatically.
  `db.sqlite3` is your local dev database; Postgres on Render starts empty.
  Register a fresh test account after deploying.
- If you ever need to wipe the *production* database, use the Shell tab:
  `python manage.py flush --no-input` (careful — this deletes everything).
