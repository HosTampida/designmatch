# DesignMatch

DesignMatch is a Flask backend plus SPA frontend deployed on Render, using PostgreSQL on Supabase.

## Architecture

- Backend: Flask + SQLAlchemy JSON API
- Frontend: plain HTML/CSS/JS SPA served from `static/`
- Database: PostgreSQL via Supabase
- Auth: token-based auth using `itsdangerous` with expiration
- Roles: `admin`, `designer`, `client`

## Core user flows

- Public users can self-register as `designer` or `client`
- Public registration requires `name`, `email`, `password`, and `role`
- Passwords are hashed with Werkzeug on the backend
- Admin-only designer imports remain protected at `/api/designers/import`
- Designers can be contacted from the SPA via WhatsApp when a phone number is available

## Auth model

- Login and registration return a bearer token
- Tokens are signed with `itsdangerous`
- Tokens expire after 1 hour
- Protected routes enforce authorization server-side

## Key files

```text
app.py
config.py
database/db.py
models/models.py
routes/auth_routes.py
routes/designer_routes.py
routes/project_routes.py
services/auth_service.py
services/matching_service.py
static/index.html
static/app.js
static/styles.css
```

## Environment

Required environment variables:

- `SECRET_KEY`
- `DATABASE_URL`

Optional admin seed variables:

- `ADMIN_EMAIL`
- `ADMIN_NAME`
- `ADMIN_PASSWORD`

## Run locally

```powershell
$env:SECRET_KEY="your-secret-key"
python app.py
```

## Production notes

- Runtime no longer executes `db.create_all()`
- Startup only runs a PostgreSQL-safe schema guard for `users.avatar_url`
- Health endpoint is available at `/api/health`
- Avatar fallback is handled in the SPA with DiceBear initials
