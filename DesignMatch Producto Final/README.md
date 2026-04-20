# DesignMatch MVP

Clean demo marketplace built with Flask, SQLite and plain HTML/CSS/JS.

## Run

```powershell
python app.py
```

Or on Windows:

```powershell
.\iniciar.bat
```

## Demo flow

1. Open `http://localhost:5000`
2. Review the seeded designer cards
3. Fill the project brief
4. Click `Find Best Designers`
5. Review ranked matches instantly

## Structure

```text
app.py
config.py
database/db.py
models/models.py
routes/auth_routes.py
routes/designer_routes.py
routes/project_routes.py
services/matching_service.py
static/index.html
static/script.js
static/styles.css
```

## Notes

- Database: `sqlite:///designmatch.db`
- Seed data loads automatically if the database is empty
- No Excel logic is used by the MVP
- No JWT or advanced auth is included
