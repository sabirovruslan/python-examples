PROJECT_NAME := otus-log-analyzer

.PHONY: build
build:
	docker build -t $(PROJECT_NAME) .

.PHONY: unit-test
unit-test: build
	docker run -it --rm ${PROJECT_NAME} python setup.py test

.PHONY: log-analyzer
log-analyzer: build
	docker run -v `pwd`:/usr/src/ -it --rm ${PROJECT_NAME} python log_analyzer.py

.PHONY: log-analyzer-config
log-analyzer-config: build
	docker run -v `pwd`:/usr/src/ -it --rm ${PROJECT_NAME} python log_analyzer.py --config ./config.cfg

.PHONY: analyze
analyze: build
	docker run -v `pwd`:/usr/src/ -it --rm ${PROJECT_NAME} python log_analyzer_func.py

.PHONY: analyze-config
analyze-config: build
	docker run -v `pwd`:/usr/src/ -it --rm ${PROJECT_NAME} python log_analyzer_func.py --config ./config.cfg