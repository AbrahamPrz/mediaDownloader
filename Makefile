SHELL := /bin/bash

venv:
	source .venv/bin/activate

run:
	python manage.py runserver

migration:
	python manage.py makemigrations

migrate:
	python manage.py migrate

superuser:
	python manage.py createsuperuser

celery:
	celery -A mysite worker -l info

deploy:
	docker compose build
	docker compose up -d