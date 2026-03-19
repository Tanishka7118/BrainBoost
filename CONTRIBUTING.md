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
HF_API_TOKEN=
HF_MODEL=HuggingFaceH4/zephyr-7b-beta
```

6. Start the app:

```bash
uvicorn app.main:app --reload --port 3000
```

## Branching and Commits

- Create feature branches from `main`.
- Keep PRs focused and reasonably small.
- Use clear commit messages in imperative mood.

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

## Coding Standards

- Follow existing code style and naming conventions.
- Keep functions focused and avoid large monolith handlers.
- Add comments only when logic is non-obvious.
- Do not commit secrets, API tokens, or local databases.

## Reporting Issues

Use the provided issue templates and include:

- clear reproduction steps
- expected vs actual behavior
- environment details (OS, Python version)
- logs and screenshots when useful

## Security

Please do not report security vulnerabilities in public issues.
Use the private disclosure process in `SECURITY.md`.
