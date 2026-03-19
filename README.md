# BrainBoost

BrainBoost is an open-source FastAPI application for student study tracking,
analytics, revision planning, and AI-assisted practice generation.

## Features

- Student registration and login with token-based auth
- Study session tracking with subject/topic granularity
- Daily, weekly, and monthly analytics endpoints
- Revision item planning and confidence-based review workflow
- Hugging Face-powered MCQ and explanation generation

## Tech Stack

- FastAPI + Starlette
- SQLAlchemy ORM + SQLite (default)
- Pydantic v2 schemas
- Jinja2 + vanilla JS frontend
- Chart.js visualizations

## Quick Start

1. Create a virtual environment and activate it.
2. Install runtime dependencies.

```bash
pip install -r requirements.txt
```

3. Create environment configuration.

```bash
cp .env.example .env
```

4. Start the app.

```bash
uvicorn app.main:app --reload --port 3000
```

5. Open the app and docs.

- UI: http://127.0.0.1:3000/login
- API docs: http://127.0.0.1:3000/docs

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

## Security and Responsible Disclosure

Please report vulnerabilities privately using the process in SECURITY.md.

## License

This project is licensed under the MIT License. See LICENSE for details.
