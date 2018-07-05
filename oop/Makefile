PROJECT_NAME := otus-oop

.PHONY: build
build:
	docker build -t $(PROJECT_NAME) .

.PHONY: unit-test
unit-test: build
	docker run -it --rm ${PROJECT_NAME} python test.py

.PHONY: oop
oop: build
	docker run -v `pwd`:/usr/src/ -it --rm ${PROJECT_NAME} python api.py

.PHONY: test
test: build
	docker run -it --rm ${PROJECT_NAME} python setup.py test