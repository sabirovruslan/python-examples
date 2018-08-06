PROJECT_NAME := otus-django

.PHONY: build
build:
	docker build -t $(PROJECT_NAME) .

.PHONY: start
start: build
	docker run -it --rm --link ${PROJECT_NAME} python manage.py runserver 0.0.0.0:8888