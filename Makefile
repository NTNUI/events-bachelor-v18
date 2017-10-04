rasmus:
	python manage.py runserver 0.0.0.0:3000

runenv:
	python3 manage.py runserver 0.0.0.0:8000

run:
	docker-compose up web

run-background:
	docker-compose up web -d

run-browser:
	docker-compose up -d selenium

stop:
	docker-compose down

test:
	docker-compose run web python manage.py test

migrations:
	docker-compose run web python manage.py makemigrations

migrate:
	docker-compose run web python manage.py migrate

superuser:
	docker-compose run web python manage.py createsuperuser

build:
	docker-compose build

testenv:
	rm -f mydatabase
	make migrate
	docker-compose run web python manage.py loaddata users.json groups.json memberships.json

browser-tests:
	docker-compose run tester python3 manage.py test ntnui.tests.browser
