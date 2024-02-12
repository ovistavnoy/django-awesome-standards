start:
	docker system prune
	docker-compose up --build

run_back:
	docker-compose up --build cache db backend

exec_back:
	docker exec -ti standards_server bash

createsuperuser:
	docker-compose run --rm backend python manage.py createsuperuser

backend_run:
	docker-compose run --rm backend bash -c "$(cmd)"

clean_all:
	docker system prune
	docker system prune -a
