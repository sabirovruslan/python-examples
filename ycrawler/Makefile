PROJECT_NAME := ycrawler

.PHONY: build
build:
	docker build -t $(PROJECT_NAME) .

.PHONY: test
test: build
	docker run -it --rm ${PROJECT_NAME} python setup.py test

.PHONY: parse
parse: build
	docker run -it --rm ${PROJECT_NAME} python ycrawler.py