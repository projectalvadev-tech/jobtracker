.PHONY: install test lint up down logs

install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt

test:
	pytest --cov=app --cov-report=term-missing

lint:
	ruff check . && ruff format --check .

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f api
