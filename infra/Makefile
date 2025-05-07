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
	docker compose --env-file ../.env exec backend python /app/utils/check_and_load_ingredients.py
	docker compose --env-file ../.env exec backend python manage.py collectstatic --noinput
	docker compose --env-file ../.env exec backend cp -r /app/collected_static/. /backend_static/static/

loaddata:
	docker compose --env-file ../.env up -d backend
	docker compose --env-file ../.env exec backend python manage.py loaddata /app/data/db_fixtures.json
	@if [ ! -d ../backend/foodgram/media ]; then echo "Error: Local media folder not found"; exit 1; fi
	docker compose --env-file ../.env cp ../backend/foodgram/media/. backend:/app/media/

dumpdata:
	docker compose --env-file ../.env up -d backend
	docker compose --env-file ../.env exec backend python manage.py dumpdata -o /app/data/db_fixtures.json
	@if [ ! -d ../backend/foodgram/data ]; then mkdir -p ../backend/foodgram/data; fi
	@if [ ! -d ../backend/foodgram/media ]; then mkdir -p ../backend/foodgram/media; fi
	docker compose --env-file ../.env cp backend:/app/data/. ../backend/foodgram/data/
	docker compose --env-file ../.env cp backend:/app/media/. ../backend/foodgram/media/

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
