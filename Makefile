.PHONY: help install run migrate migrate-create migrate-upgrade migrate-downgrade db-create clean lint format test

help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies with UV"
	@echo "  make run              - Run the development server"
	@echo "  make migrate          - Create and apply database migrations"
	@echo "  make migrate-create   - Create a new migration (use MSG='description')"
	@echo "  make migrate-upgrade  - Apply pending migrations"
	@echo "  make migrate-downgrade- Rollback last migration"
	@echo "  make db-create        - Create database and user in PostgreSQL"
	@echo "  make clean            - Remove cache and temporary files"
	@echo "  make format           - Format code with ruff"
	@echo "  make lint             - Lint code with ruff"

install:
	uv sync

run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate: migrate-create migrate-upgrade

migrate-create:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: Please provide a migration message using MSG='your message'"; \
		echo "Example: make migrate-create MSG='add user table'"; \
		exit 1; \
	fi
	uv run alembic revision --autogenerate -m "$(MSG)"

migrate-upgrade:
	uv run alembic upgrade head

migrate-downgrade:
	uv run alembic downgrade -1

migrate-history:
	uv run alembic history

db-create:
	@echo "Creating database and user in PostgreSQL..."
	@echo "Run the following SQL commands in your PostgreSQL client:"
	@echo ""
	@echo "CREATE DATABASE todo_db;"
	@echo "CREATE USER strapi WITH PASSWORD 'strapi_password';"
	@echo "GRANT ALL PRIVILEGES ON DATABASE todo_db TO strapi;"
	@echo ""
	@echo "Or run with psql:"
	@echo 'psql -U postgres -c "CREATE DATABASE todo_db;"'
	@echo 'psql -U postgres -c "CREATE USER strapi WITH PASSWORD '\''strapi_password'\'';"'
	@echo 'psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE todo_db TO strapi;"'

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

format:
	uv run ruff format .

lint:
	uv run ruff check .

dev: install migrate-upgrade run

shell:
	uv run python

psql:
	psql -U strapi -d todo_db

test:
	uv run pytest -v
