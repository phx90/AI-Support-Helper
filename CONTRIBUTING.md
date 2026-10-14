# Contributing

Thank you for improving AI Support Hub. Keep pull requests focused, explain the user-visible outcome, and never commit credentials, personal data, or proprietary support documents.

## Local setup

1. Copy `.env.example` to `.env`.
2. Start the complete stack with `docker compose up --build -d`.
3. Open the web app at `http://localhost:3000` and Swagger at `http://localhost:8000/docs`.
4. Use the deterministic mock mode unless a provider integration is specifically under test.

## Quality checks

Run the same checks used by CI before opening a pull request:

```bash
cd backend
ruff format --check .
ruff check .
pytest --cov=app --cov-report=term-missing --cov-fail-under=80

cd ../frontend
npm ci
npm run format:check
npm run lint
npm run typecheck
npm run build
```

You can also use `make check` when GNU Make and Docker are available.

## Database changes

Create an Alembic migration for every schema change. Confirm both a clean installation and an upgrade from the previous schema work before submitting the change.

## Pull requests

- Link the issue or explain the motivation.
- Add or update tests for changed behavior.
- Update documentation and `.env.example` for public configuration changes.
- Include screenshots for meaningful interface changes.
- Keep generated output, local uploads, `.env`, and provider credentials out of Git.

By participating, you agree to keep discussion constructive, respectful, and focused on the project.
