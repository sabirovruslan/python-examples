PROJECT_NAME := otus-log-analyzer

build:
	docker build -t $(PROJECT_NAME) .