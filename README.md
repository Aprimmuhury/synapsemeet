# SynapseMeet

SynapseMeet is an AI-powered meeting mobile app: schedule meetings, join by
room code, chat, track AI-detected action items, and get an AI-generated
meeting summary — all from a mobile-first web app that installs like a
native app (PWA).

```text
synapsemeet/
├── backend/            Python + Django REST API (SQL database via Django ORM)
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── synapsemeet/    Django project (settings, urls, wsgi/asgi)
│   ├── accounts/       User registration, login (JWT), profile
│   ├── meetings/       Meetings, participants, chat, action items
│   └── ai_assistant/   Transcript storage + AI summary generation
└── frontend/           HTML + CSS + JavaScript mobile app (PWA)
    ├── index.html          Sign in
    ├── register.html       Create account
    ├── dashboard.html      Meeting list, join by code, schedule (FAB)
    ├── meeting-create.html Schedule a new meeting
    ├── meeting-room.html   Live meeting: participants, AI panel, chat, actions
    ├── profile.html        Account settings
    ├── css/style.css        Core design system ("synapse pulse" identity)
    ├── css/responsive.css   Breakpoints
    ├── js/api.js            Fetch wrapper + JWT handling for the Django API
    ├── js/auth.js            Login / register screen logic
    ├── js/dashboard.js       Dashboard screen logic
    ├── js/meeting.js         Meeting room logic
    ├── js/ai-assistant.js    Live caption rendering helpers
    ├── js/sw-register.js     Registers the service worker
    ├── service-worker.js     Offline app-shell caching
    ├── manifest.json         PWA manifest (installable mobile app)
    └── assets/icons/synapse-logo.svg
```

## 1. Backend setup (Python / Django / SQL)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then edit .env (SECRET_KEY, AI_API_KEY, ...)

python manage.py migrate         # creates db.sqlite3 (SQL database)
python manage.py createsuperuser # optional, for /admin/
python manage.py runserver       # http://127.0.0.1:8000
```

The database is SQLite by default (a real SQL database, zero extra setup).
For Google Cloud, use **Cloud SQL for PostgreSQL**. The same Django models,
serializers, API endpoints, and frontend behavior continue to work because
they all use the Django ORM.

Set these values in `backend/.env`:

```env
DB_ENGINE=cloudsql
DB_NAME=synapsemeet
DB_USER=postgres
DB_PASSWORD=your-cloud-sql-password
DB_HOST=127.0.0.1
DB_PORT=5432
DB_SSLMODE=require
```

`DB_HOST` should be `127.0.0.1` when using the Cloud SQL Auth Proxy locally.
For a deployed service using the Cloud SQL Unix socket, set it to the socket
directory, for example `/cloudsql/project-id:region:instance-id`.
After installing requirements, run `python manage.py migrate` to create the
same tables in Cloud SQL. Keep `DB_ENGINE=sqlite` when working locally without
Cloud SQL.

### API overview

| Endpoint | Purpose |
| --- | --- |
| `POST /api/auth/register/` | Create an account |
| `POST /api/auth/login/` | Get JWT access/refresh tokens |
| `GET/PATCH /api/auth/me/` | Current user |
| `GET/PATCH /api/auth/profile/` | SynapseMeet profile settings |
| `GET/POST /api/meetings/` | List / schedule meetings |
| `POST /api/meetings/{id}/join/` | Join a meeting |
| `POST /api/meetings/join_by_code/` | Join via room code |
| `POST /api/meetings/{id}/start/` `/end/` | Host controls |
| `GET/POST /api/meetings/{id}/chat/` | In-meeting chat |
| `GET/POST /api/meetings/{id}/action-items/` | Follow-up tasks |
| `POST /api/ai/meetings/{id}/transcript/` | Stream live speech-to-text chunks |
| `GET/POST /api/ai/meetings/{id}/summary/` | Fetch / generate the AI summary |

## 2. Frontend setup (HTML / CSS / JavaScript)

The frontend and backend can run together from Django. After the backend setup
above, open `http://127.0.0.1:8000/`; Django serves the HTML/CSS/JavaScript and
the frontend automatically calls `/api/...` on the same origin. API responses
are rendered by the existing page scripts.

For frontend-only development, the separate static server remains available:

The frontend is static, so any web server works. Simplest option:

```bash
cd frontend
python -m http.server 5500
# open http://127.0.0.1:5500
```

By default the frontend calls the backend at `http://127.0.0.1:8000/api`.
To change that, set it before the other scripts load, e.g. add this to the
`<head>` of any page:

```html
<script>window.SYNAPSEMEET_API_BASE = "https://your-backend-domain.com/api";</script>
```

Because `manifest.json` + `service-worker.js` are included, opening the
frontend in a mobile browser (Chrome/Safari) and choosing **"Add to Home
Screen"** installs SynapseMeet as a standalone mobile app icon.

## 3. Wiring up real AI

`backend/ai_assistant/services.py` is the single integration point for a
real LLM provider (Anthropic, OpenAI, etc.). Right now `_call_llm()` returns
a clearly-labeled placeholder so the whole app runs end-to-end without an
API key. Set `AI_API_KEY` in `backend/.env` and follow the instructions in
that file's docstring to plug in a live call.

Live audio transcription and video/audio transport (WebRTC) are also left
as clean integration points — see the comments in `frontend/js/meeting.js`
(`initMedia()`) and `ai_assistant/services.py` — since those require an
external provider (e.g. LiveKit/Daily for video, a speech-to-text API for
captions) rather than something that can be meaningfully faked.

## Design notes

The interface uses a dark "ink" canvas with a signature **synapse pulse**:
an animated violet-to-cyan ring that lights up around any participant tile
that is currently speaking, echoing the product's neural/AI theme without
relying on decoration for its own sake.

for clear database:
cd backend;
python manage.py flush --no-input ;
