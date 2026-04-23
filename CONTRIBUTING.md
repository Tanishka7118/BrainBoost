# Contributing to BrainBoost

Thank you for your interest in improving BrainBoost.
This guide explains how to contribute effectively and consistently.

## Development Setup

1. Fork and clone the repository.
2. Create and activate a virtual environment.
3. Install runtime dependencies:

```bash
pip install -r requirements.txt
```

4. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

5. Configure environment variables in a local `.env` file:

```env
SECRET_KEY=replace-me
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=postgresql+psycopg://postgres:<password>@localhost:5432/brainboost
HF_API_TOKEN=
HF_MODEL=HuggingFaceH4/zephyr-7b-beta
```

If your Postgres user can create databases, BrainBoost auto-creates `brainboost` on startup.
Otherwise create it manually before running the app.

6. Start the app:

```bash
uvicorn app.main:app --reload --port 3000
```

7. (Optional) Seed local demo data:

```bash
python scripts/seed_demo_data.py
```

Demo credentials for local validation:

- Email: `tanishka@example.com`
- Password: `Pass@123`

### Notes for First-Time Contributors

- Check existing open issues before starting work.
- Ask clarifying questions early in issue comments when requirements are ambiguous.
- Prefer small, focused PRs over one large multi-topic PR.

## Branching and Commits

- Create feature branches from `main`.
- Keep PRs focused and reasonably small.
- Use clear commit messages in imperative mood.

Recommended branch names:

- `feat/<short-topic>`
- `fix/<short-topic>`
- `docs/<short-topic>`
- `test/<short-topic>`

Suggested format:

- `feat: add revision due date validation`
- `fix: handle empty analytics result`
- `docs: improve local setup instructions`

## Pull Request Checklist

Before opening a PR, verify:

- Tests pass locally: `pytest`
- Lint checks pass locally: `ruff check .`
- Code formatting is clean: `ruff format .`
- New behavior includes tests where applicable
- API or user-facing changes are documented in `README.md`
- Contributor-facing behavior changes are documented in `CONTRIBUTING.md` when relevant
- Changelog updated under `Unreleased` for notable changes
- PR description includes repro steps (bug fix) or acceptance checks (feature)

## What Maintainers Look For

- Clear problem statement in PR description
- Minimal, focused diff with no unrelated formatting churn
- Backward compatibility for existing endpoints unless explicitly discussed
- Reasonable tests for bug fixes and behavior changes

## Coding Standards

- Follow existing code style and naming conventions.
- Keep functions focused and avoid large monolith handlers.
- Add comments only when logic is non-obvious.
- Do not commit secrets, API tokens, or local databases.

Frontend/UI contributions:

- Keep responsive behavior intact (desktop + mobile)
- Preserve existing visual style unless the PR is explicitly a redesign
- Validate key flows on `/dashboard` and `/revision`

Backend/API contributions:

- Preserve existing route compatibility unless discussed with maintainers
- Avoid introducing breaking schema assumptions for contributor/dev environments
- Add or update tests in `tests/` for behavior changes

## Reporting Issues

Use the provided issue templates and include:

- clear reproduction steps
- expected vs actual behavior
- environment details (OS, Python version)
- logs and screenshots when useful

## Security

Please do not report security vulnerabilities in public issues.
Use the private disclosure process in `SECURITY.md`.
