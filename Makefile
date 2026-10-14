.PHONY: up down build logs test lint format-check frontend-check check migrate seed

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

test:
	docker compose run --rm backend pytest --cov=app --cov-report=term-missing --cov-fail-under=80

lint:
	docker compose run --rm backend ruff check .
	docker compose run --rm frontend npm run lint

format-check:
	docker compose run --rm backend ruff format --check .

frontend-check:
	docker compose run --rm frontend sh -c "npm run format:check && npm run lint && npm run typecheck && npm run build"

check: format-check lint test frontend-check

migrate:
	docker compose run --rm backend alembic upgrade head

seed:
	docker compose run --rm backend python scripts/seed.py
