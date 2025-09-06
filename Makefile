# Makefile para Currículos IA

.PHONY: install migrate run test lint tailwind

install:
	pip install -r requirements.txt

migrate:
	python manage.py migrate

run:
	python manage.py runserver

test:
	python manage.py test

lint:
	flake8 .

tailwind:
	python manage.py tailwind start

collectstatic:
	python manage.py collectstatic --noinput

superuser:
	python manage.py createsuperuser

shell:
	python manage.py shell

setup: install migrate
