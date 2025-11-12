.PHONY: run migrate shell test format lint

run:
	uv run python manage.py runserver

migrate:
	uv run python manage.py makemigrations
	uv run python manage.py migrate

shell:
	uv run python manage.py shell

test:
	uv run python manage.py test

format:
	uv run ruff format .

lint:
	uv run ruff check . --fix
