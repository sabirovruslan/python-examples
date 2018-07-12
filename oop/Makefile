PROJECT_NAME := otus-oop

.PHONY: build
build:
	docker build -t $(PROJECT_NAME) .

.PHONY: memcached
memcached:
	docker run -d -p 127.0.0.1:11211:11211 --name store memcached

.PHONY: test
test: build
	docker run -it --rm --link store:store ${PROJECT_NAME} python setup.py test