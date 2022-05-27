BACKEND_SERVICE = backend
BACKEND_IMAGE = ridmel/foodgram_backend:latest
FRONTEND_IMAGE = ridmel/foodgram_frontend:latest

refresh_images:
	docker pull --quiet $(BACKEND_IMAGE) \
	&& docker pull --quiet $(FRONTEND_IMAGE) \

run_new:
	make refresh_images \
	&& docker compose up -d \
	&& sleep 5 \
	&& docker compose exec $(BACKEND_SERVICE) python manage.py migrate \
	&& docker compose exec $(BACKEND_SERVICE) python manage.py collectstatic --no-input

run_demo:
	cp .env.example .env \
	&& make run_new \
	&& docker compose cp ../data/demo_db_dump/pictures_for_django_media/. $(BACKEND_SERVICE):/app/django_media/ \
	&& docker compose cp ../data/demo_db_dump/foodgram_dump.json $(BACKEND_SERVICE):/app/ \
	&& docker compose exec $(BACKEND_SERVICE) python manage.py loaddata foodgram_dump.json

create_user:
	docker compose exec $(BACKEND_SERVICE) python manage.py createsuperuser

down:
	docker compose down -v
