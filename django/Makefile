PROJECT_NAME := otus-django

.PHONY: build
build:
	docker build -t $(PROJECT_NAME) .

.PHONY: start
start: build
	docker run -it --rm -v `pwd`:/usr/src  ${PROJECT_NAME} bash