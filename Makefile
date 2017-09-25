env-run:
	python3 manage.py runserver 0.0.0.0:8000

run:
	docker-compose up

run-background:
	docker-compose up -d

stop:
	docker-compose down

migrations:
	docker-compose run web python manage.py makemigrations

migrate:
	docker-compose run web python manage.py migrate

superuser:
	docker-compose run web python manage.py createsuperuser
