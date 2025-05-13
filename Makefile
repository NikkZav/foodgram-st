# infra/Makefile
.PHONY: up down clear collectstatic download-media-and-static migrate load-ingredients load-fixtures dumpdata build rebuild start stop setup setup-with-data setup-without-data delete createsuperuser create-env

# Создание .env из .env.example
create-env:
	@if [ ! -f .env.example ]; then echo "Error: .env.example file not found"; exit 1; fi
	@if [ -f .env ]; then echo "Warning: .env already exists, skipping"; else cp .env.example .env; fi

up:
	docker compose --env-file .env up -d

down:
	docker compose --env-file .env down

clear:
	docker compose --env-file .env down -v

collectstatic:
	docker compose --env-file .env exec backend python manage.py collectstatic --noinput
	docker compose --env-file .env exec backend cp -r /app/collected_static/. /backend_static/static/

# Скачивание и распаковка медиа и статики
download-media-and-static:
	@if [ ! -f .env ]; then echo "Error: .env file not found"; exit 1; fi
	$(eval include .env)
	$(eval export)
	wget --no-check-certificate -O data.zip "$$DATA_ZIP_URL"
	@if [ `file data.zip | grep -c "Zip archive"` -eq 0 ]; then echo "Error: Downloaded file is not a valid ZIP archive"; rm data.zip; exit 1; fi
	unzip -o data.zip -d backend/foodgram/
	rm data.zip

migrate:
	@if [ ! -f .env ]; then echo "Error: .env file not found"; exit 1; fi
	$(eval include .env)
	$(eval export)
	docker compose --env-file .env exec backend bash -c "until nc -z $$DB_HOST $$DB_PORT; do echo 'Waiting for $$DB_HOST:$$DB_PORT...'; sleep 1; done"
	docker compose --env-file .env exec backend python manage.py makemigrations
	docker compose --env-file .env exec backend python manage.py migrate

load-ingredients:
	docker compose --env-file .env exec backend python manage.py import_ingredients /app/data/db_ingredients.json

load-fixtures:
	docker compose --env-file .env up -d backend
	docker compose --env-file .env exec backend python manage.py loaddata /app/data/db_fixtures.json
	@if [ ! -d ./backend/foodgram/media ]; then echo "Error: Local media folder not found"; exit 1; fi
	docker compose --env-file .env cp ./backend/foodgram/media/. backend:/app/media/

dumpdata:
	docker compose --env-file .env up -d backend
	docker compose --env-file .env exec backend python manage.py dumpdata -o /app/data/db_fixtures.json
	@if [ ! -d ./backend/foodgram/data ]; then mkdir -p ./backend/foodgram/data; fi
	@if [ ! -d ./backend/foodgram/media ]; then mkdir -p ./backend/foodgram/media; fi
	docker compose --env-file .env cp backend:/app/data/. ./backend/foodgram/data/
	docker compose --env-file .env cp backend:/app/media/. ./backend/foodgram/media/

build:
	docker compose --env-file .env build --no-cache

rebuild:
	docker compose --env-file .env stop && docker compose --env-file .env up -d --build

start:
	docker compose --env-file .env start

stop:
	docker compose --env-file .env stop

setup:
	make build
	make up
	make collectstatic
	make migrate

setup-with-data:
	make download-media-and-static
	make setup
	make load-fixtures

setup-without-data:
	make setup
	make load-ingredients

delete:
	make down
	make clear

createsuperuser:
	docker compose --env-file .env exec backend python manage.py createsuperuser
