.PHONY: install services migrate seed-demo reset-demo up verify contract build

install:
	pnpm install --frozen-lockfile
	uv sync --locked --all-packages

services:
	docker compose up -d --wait postgres redis

migrate:
	cd apps/api && uv run alembic upgrade head
	cd apps/api && uv run python -m src.platform.bootstrap_checkpointer
	docker compose run --rm gateway-migrate

seed-demo:
	cd apps/api && uv run python -m src.platform.seed_demo

reset-demo:
	cd apps/api && uv run python -m src.platform.seed_demo --reset

up:
	docker compose up -d --wait

verify:
	uv run --project apps/api ruff check apps/api scripts
	uv run --project apps/api ruff format --check apps/api scripts
	uv run --project apps/api mypy --strict apps/api/src/modules/ideas/domain apps/api/src/modules/iterations/domain apps/api/src/modules/constraint_analysis/domain apps/api/src/modules/profiles/domain apps/api/src/modules/company_context/domain
	cd apps/api && uv run pytest -m 'not live'
	pnpm lint
	pnpm typecheck
	node scripts/check_locales.mjs

contract:
	cd apps/api && uv run python -m src.platform.export_openapi
	pnpm generate:client

build:
	docker compose build
