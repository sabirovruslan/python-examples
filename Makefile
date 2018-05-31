PROJECT_NAME := otus-log-analyzer

.PHONY: build
build:
	docker build -t $(PROJECT_NAME) .

.PHONY: unit-test
unit-test: build
	docker run -it --rm ${PROJECT_NAME} python setup.py test

.PHONY: log-analyzer
log-analyzer: build
	docker run -it --rm ${PROJECT_NAME} python log_analyzer.py

.PHONY: log-analyzer-config
log-analyzer-config: build
	docker run -it --rm ${PROJECT_NAME} python log_analyzer.py --config ./config.cfg