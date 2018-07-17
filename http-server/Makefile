PROJECT_NAME := otus-http-server

.PHONY: build
build:
	docker build -t $(PROJECT_NAME) .

.PHONY: server
server: build
	docker rm -f server || true
	docker run -it --rm -p 80:80 -h http-server --name server ${PROJECT_NAME} python httpd.py