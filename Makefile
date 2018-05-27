PROJECT_NAME := otus-log-analyzer

.PHONY: build
build:
	docker build -t $(PROJECT_NAME) .

.PHONY: unit-test
unit-test: build
	docker run -it --rm ${PROJECT_NAME} python setup.py test