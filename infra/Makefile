# infra/Makefile
.PHONY: up down init build setup

up:
	docker compose --env-file ../.env up -d

down:
	docker compose --env-file ../.env down

clear:
	docker compose --env-file ../.env down -v

init:
	@if [ ! -f ../.env ]; then echo "Error: .env file not found"; exit 1; fi
	$(eval include ../.env)
	$(eval export)
	docker compose --env-file ../.env exec backend bash -c "until nc -z $$DB_HOST $$DB_PORT; do echo 'Waiting for $$DB_HOST:$$DB_PORT...'; sleep 1; done"
	docker compose --env-file ../.env exec backend python manage.py makemigrations
	docker compose --env-file ../.env exec backend python manage.py migrate
	docker compose --env-file ../.env exec backend python /app/utils/check_ingredients.py
	docker compose --env-file ../.env exec backend python manage.py collectstatic --noinput
	docker compose --env-file ../.env exec backend cp -r /app/collected_static/. /backend_static/static/

build:
	docker compose --env-file ../.env build --no-cache

rebuild:
	docker compose --env-file ../.env stop && docker compose --env-file ../.env up -d --build

start:
	docker compose --env-file ../.env start

stop:
	docker compose --env-file ../.env stop

setup:
	make build
	make up
	make init

delete:
	make down
	make clear

createsuperuser:
	docker compose --env-file ../.env exec backend python manage.py createsuperuser
