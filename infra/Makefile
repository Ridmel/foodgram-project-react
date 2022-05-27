BACKEND_SERVICE = backend

run_new:
	docker compose up -d \
	&& docker compose exec $(BACKEND_SERVICE) python manage.py migrate \
	&& docker compose exec $(BACKEND_SERVICE) python manage.py collectstatic --no-input

run_demo:
	cp .env.example .env \
	&& make run_new \
	&& sleep 5 \
	&& docker compose cp ../data/demo_db_dump/pictures_for_django_media/. $(BACKEND_SERVICE):/app/django_media/ \
	&& docker compose cp ../data/demo_db_dump/foodgram_dump.json $(BACKEND_SERVICE):/app/ \
	&& docker compose exec $(BACKEND_SERVICE) python manage.py loaddata foodgram_dump.json

create_user:
	docker compose exec $(BACKEND_SERVICE) python manage.py createsuperuser

down:
	docker compose down -v
