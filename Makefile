default: up

build:
	docker-compose build --no-cache --force-rm
	docker-compose up -d db api
	docker-compose exec api wait-for db:3306 -t 30 -- python manage.py makemigrations
	docker-compose exec api python manage.py migrate
	docker-compose down

logs:
	docker-compose logs -f

up:
	docker-compose up --force-recreate -d

test:
	# RUN pylint inside api
	docker-compose exec api wait-for db:3306 -t 30 -- python manage.py test api

clean:
	docker-compose down -v --remove-orphans

proper:
	docker-compose down -v --remove-orphans --rmi all
