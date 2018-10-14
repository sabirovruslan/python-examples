PROJECT_NAME := goland

.PHONY: build
build:
	docker build -t $(PROJECT_NAME) .

.PHONY: load
load: build
	docker run -it --rm ${PROJECT_NAME}