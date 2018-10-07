PROJECT_NAME := ycrawler

.PHONY: build
build:
	docker build -t $(PROJECT_NAME) .

.PHONY: parse
parse: build
	docker run -it --rm -v `pwd`:/usr/src/ ${PROJECT_NAME} python ycrawler.py