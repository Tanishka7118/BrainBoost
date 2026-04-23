# BrainBoost

BrainBoost is an open-source FastAPI application for student study tracking,
analytics, revision planning, and AI-assisted practice generation.

This repository is PostgreSQL-first and ready for direct contributor onboarding.

## Features

- Student registration and login with token-based auth
- Study session tracking with subject/topic granularity
- Daily, weekly, and monthly analytics endpoints
- Revision item planning and confidence-based review workflow
- Hugging Face-powered MCQ and explanation generation
- Profile-aware UI with authenticated user menu

## Tech Stack

- FastAPI + Starlette
- SQLAlchemy ORM + PostgreSQL (default)
- Pydantic v2 schemas
- Jinja2 + vanilla JS frontend
- Chart.js visualizations

## Quick Start

1. Clone the repository.
2. Create a virtual environment and activate it.
3. Install runtime dependencies.

```bash
pip install -r requirements.txt
```

Windows (PowerShell) venv activation example:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Create environment configuration.

```bash
cp .env.example .env
```

Default database URL:

```env
DATABASE_URL=postgresql+psycopg://postgres:qwerty@localhost:5432/brainboost
```

4. Create the PostgreSQL database if your role cannot create databases.

```sql
CREATE DATABASE brainboost;
```

If your PostgreSQL role has permission to create databases, BrainBoost will create `brainboost` automatically on first startup.

5. Start the app.

```bash
uvicorn app.main:app --reload --port 3000
```

6. Open the app and docs.

- UI: http://127.0.0.1:3000/login
- API docs: http://127.0.0.1:3000/docs

## Standalone Database Model

- BrainBoost is configured for PostgreSQL as the primary database.
- There is no migration workflow required for new contributor setup.
- Run the app once and tables are created automatically.

## Seed Demo Data

To populate development data (including a user, sessions, revisions, and generated questions):

```bash
python scripts/seed_demo_data.py
```

Seeded credentials:

- Email: `tanishka@example.com`
- Password: `Pass@123`

## Development

Install developer tooling:

```bash
pip install -r requirements-dev.txt
```

Run checks:

```bash
ruff check .
ruff format .
pytest
```

Recommended pre-PR check sequence:

```bash
ruff check .
ruff format .
pytest
```

## API and Page Routes (High Level)

- Auth: `/auth/register`, `/auth/login`, `/auth/me`
- Study sessions: `/sessions/`
- Analytics: `/analytics/overview`, `/analytics/daily`, `/analytics/weekly`, `/analytics/monthly`
- Revision: `/revisions/`, `/revisions/due`, `/revisions/{item_id}/review`
- AI practice: `/practice/generate`, `/explain`, `/assessment`
- Pages: `/login`, `/register`, `/dashboard`, `/revision`

Legacy `/api/...` aliases are kept for compatibility.

## Project Layout

```
app/
  core/         # config and security
  db/           # engine/session setup
  models/       # SQLAlchemy entities
  routers/      # API and page routers
  schemas/      # request/response models
  services/     # analytics and AI integration
  static/       # css/js assets
  templates/    # server-side rendered pages
  main.py       # FastAPI entrypoint
tests/          # automated tests
.github/        # issue templates + CI workflow
```

## Contributing

Contributions are welcome. Please read:

- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- SECURITY.md

For first-time contributors, start with documentation, tests, or small bug fixes before larger refactors.

Suggested first contribution areas:

- docs clarity and examples
- test coverage for routers/services
- UX polish on `/dashboard` and `/revision`

## Security and Responsible Disclosure

Please report vulnerabilities privately using the process in SECURITY.md.

## License

This project is licensed under the MIT License. See LICENSE for details.
