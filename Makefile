SHELL := /bin/bash

venv:
	source .venv/bin/activate

run:
	python3 manage.py runserver

migration:
	python3 manage.py makemigrations

migrate:
	python3 manage.py migrate

superuser:
	python3 manage.py createsuperuser

celery:
	celery -A mysite worker -l info

deploy:
	docker compose build
	docker compose up -d