PROJECT_NAME := otus-oop

.PHONY: build
build:
	docker build -t $(PROJECT_NAME) .

.PHONY: clean
clean:
	docker rm -f store || true

.PHONY: memcached
memcached: clean
	docker run -d -p 127.0.0.1:11211:11211 --name store memcached

.PHONY: oop
oop: build memcached
	docker run -v `pwd`:/usr/src/ -it --rm -p 127.0.0.1:8080:8080 --link store:store ${PROJECT_NAME} python api.py

.PHONY: test
test: build memcached
	docker run -it --rm --link store:store ${PROJECT_NAME} python setup.py test