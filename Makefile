PROJECT_NAME := otus-log-analyzer

log:
	docker exec ${PROJECT_NAME} python log_analyzer.py