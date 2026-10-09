.PHONY: help dev build test lint helm-lint clean

help:
	@echo "Urumi AI Platform - Development Commands"
	@echo "========================================="
	@echo "  make dev         - Launch all services with Docker Compose"
	@echo "  make build       - Build all Docker images"
	@echo "  make test        - Run Python test suite"
	@echo "  make helm-lint   - Validate Kubernetes Helm charts"
	@echo "  make clean       - Remove temporary artifacts and caches"

dev:
	docker compose up --build

build:
	docker compose build

test:
	pytest -v

helm-lint:
	helm lint helm/woocommerce
	helm lint helm/urumi-platform

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf dashboard/dist
