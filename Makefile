# Audio Processing System - Linux Makefile
# Comprehensive build and test automation

.PHONY: help setup install test clean docker docker-up docker-down lint format check coverage docs

# Default target
.DEFAULT_GOAL := help

# Colors for output
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Project configuration
PROJECT_NAME := audio-processing-system
PYTHON := python3
PIP := pip3
VENV_PATH := .venv
DOCKER_IMAGE := audio-processing-tests
DOCKER_COMPOSE := docker-compose

help: ## Show this help message
	@echo "$(GREEN)Audio Processing System - Make Commands$(RESET)"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}'

# Setup and Installation
setup: ## Initial setup for Linux systems
	@echo "$(GREEN)Setting up Audio Processing System...$(RESET)"
	@chmod +x scripts/*.sh
	@./scripts/setup.sh

install: ## Install dependencies in existing virtual environment
	@echo "$(GREEN)Installing dependencies...$(RESET)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r pytest/requirements.txt

install-dev: ## Install development dependencies
	@echo "$(GREEN)Installing development dependencies...$(RESET)"
	@$(PIP) install -r pytest/requirements.txt
	@$(PIP) install black flake8 mypy isort pre-commit

# Testing
test: ## Run working tests (no missing modules)
	@echo "$(GREEN)Running working tests...$(RESET)"
	@python pytest/run_working_tests.py

test-mocked: ## Run all tests with mocked modules
	@echo "$(GREEN)Running all tests with mocks...$(RESET)"
	@cd pytest && python -m pytest -v --tb=short -p no:postgresql -p no:kubernetes

test-demo: ## Run demo tests only
	@echo "$(GREEN)Running demo tests...$(RESET)"
	@./scripts/run_tests.sh demo

test-unit: ## Run unit tests
	@echo "$(GREEN)Running unit tests...$(RESET)"
	@./scripts/run_tests.sh unit --verbose

test-functional: ## Run functional tests
	@echo "$(GREEN)Running functional tests...$(RESET)"
	@./scripts/run_tests.sh functional

test-performance: ## Run performance tests
	@echo "$(GREEN)Running performance tests...$(RESET)"
	@./scripts/run_tests.sh performance

test-security: ## Run security tests
	@echo "$(GREEN)Running security tests...$(RESET)"
	@./scripts/run_tests.sh security

test-all: ## Run all tests
	@echo "$(GREEN)Running all tests...$(RESET)"
	@./scripts/run_tests.sh all --parallel

coverage: ## Generate coverage report
	@echo "$(GREEN)Generating coverage report...$(RESET)"
	@./scripts/run_tests.sh coverage --parallel
	@echo "$(YELLOW)Coverage report available at: coverage_html/index.html$(RESET)"

# Docker operations
docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(RESET)"
	@docker build -t $(DOCKER_IMAGE) .

docker-run: ## Run tests in Docker container
	@echo "$(GREEN)Running tests in Docker...$(RESET)"
	@docker run --rm -v $(PWD)/test-reports:/app/test-reports $(DOCKER_IMAGE)

docker-up: ## Start full Docker environment
	@echo "$(GREEN)Starting Docker environment...$(RESET)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(YELLOW)Services available:$(RESET)"
	@echo "- PostgreSQL: localhost:5432"
	@echo "- Redis: localhost:6379"
	@echo "- RabbitMQ: localhost:5672 (Management: http://localhost:15672)"

docker-up-monitoring: ## Start Docker environment with monitoring
	@echo "$(GREEN)Starting Docker environment with monitoring...$(RESET)"
	@$(DOCKER_COMPOSE) --profile monitoring up -d
	@echo "$(YELLOW)Additional services:$(RESET)"
	@echo "- Prometheus: http://localhost:9090"
	@echo "- Grafana: http://localhost:3000 (admin/admin)"

docker-down: ## Stop Docker environment
	@echo "$(GREEN)Stopping Docker environment...$(RESET)"
	@$(DOCKER_COMPOSE) down

docker-clean: ## Clean Docker environment and volumes
	@echo "$(GREEN)Cleaning Docker environment...$(RESET)"
	@$(DOCKER_COMPOSE) down -v --remove-orphans
	@docker image rm $(DOCKER_IMAGE) 2>/dev/null || true

# Code Quality
lint: ## Run linting checks
	@echo "$(GREEN)Running linting checks...$(RESET)"
	@$(PYTHON) -m flake8 pytest/ --max-line-length=100 --ignore=E203,W503
	@$(PYTHON) -m mypy pytest/ --ignore-missing-imports || true

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(RESET)"
	@$(PYTHON) -m black pytest/ --line-length=100
	@$(PYTHON) -m isort pytest/ --profile black

format-check: ## Check code formatting
	@echo "$(GREEN)Checking code formatting...$(RESET)"
	@$(PYTHON) -m black pytest/ --check --line-length=100
	@$(PYTHON) -m isort pytest/ --check-only --profile black

# Environment management
venv: ## Create virtual environment
	@echo "$(GREEN)Creating virtual environment...$(RESET)"
	@$(PYTHON) -m venv $(VENV_PATH)
	@echo "$(YELLOW)Activate with: source $(VENV_PATH)/bin/activate$(RESET)"

clean: ## Clean temporary files and cache
	@echo "$(GREEN)Cleaning temporary files...$(RESET)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf coverage_html/ .coverage test-reports/ logs/ performance_results/

clean-all: clean docker-clean ## Clean everything including Docker
	@echo "$(GREEN)Deep cleaning...$(RESET)"
	@rm -rf $(VENV_PATH)

# Documentation
docs: ## Generate documentation
	@echo "$(GREEN)Generating documentation...$(RESET)"
	@mkdir -p docs/_build
	@echo "Documentation structure:" > docs/_build/index.txt
	@find docs/ -name "*.md" | sort >> docs/_build/index.txt

# Health checks
check: ## Run system health checks
	@echo "$(GREEN)Running system health checks...$(RESET)"
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Pip version: $$($(PIP) --version)"
	@echo "Virtual environment: $${VIRTUAL_ENV:-Not activated}"
	@echo "Project structure:"
	@ls -la
	@echo "$(GREEN)Running basic test to verify setup...$(RESET)"
	@$(PYTHON) pytest/demo_test.py

check-docker: ## Check Docker environment
	@echo "$(GREEN)Checking Docker environment...$(RESET)"
	@docker --version
	@docker-compose --version
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# System dependencies
linux-deps: ## Install Linux system dependencies (Ubuntu/Debian)
	@echo "$(GREEN)Installing Linux system dependencies...$(RESET)"
	@sudo apt-get update
	@sudo apt-get install -y python3-dev python3-pip python3-venv
	@sudo apt-get install -y libpq-dev postgresql-client
	@sudo apt-get install -y redis-tools
	@sudo apt-get install -y build-essential gcc

# CI/CD helpers
ci-test: ## Run tests for CI environment
	@echo "$(GREEN)Running CI tests...$(RESET)"
	@$(PYTHON) -m pytest pytest/ --tb=short -v \
		--junit-xml=test-results.xml \
		--cov=pytest \
		--cov-report=xml:coverage.xml \
		--cov-report=html:coverage_html \
		-p no:postgresql -p no:kubernetes

# Monitoring and logs
logs: ## Show recent logs
	@echo "$(GREEN)Recent system logs:$(RESET)"
	@tail -n 50 logs/*.log 2>/dev/null || echo "No logs found"

monitor: ## Show system resources
	@echo "$(GREEN)System resources:$(RESET)"
	@echo "Memory usage:"
	@free -h
	@echo "Disk usage:"
	@df -h .
	@echo "Process info:"
	@ps aux | grep python | head -5

# Development workflow
dev-setup: setup install-dev ## Complete development setup
	@echo "$(GREEN)Development environment ready!$(RESET)"

dev-test: format lint test-all coverage ## Complete development test cycle
	@echo "$(GREEN)Development test cycle completed!$(RESET)"

# Quick commands
quick-test: ## Quick test (demo only)
	@$(PYTHON) pytest/demo_test.py

quick-setup: ## Quick setup for demonstration
	@./scripts/setup.sh
	@./scripts/run_tests.sh demo

# Information
info: ## Show project information
	@echo "$(GREEN)Audio Processing System Information$(RESET)"
	@echo "=================================="
	@echo "Project: $(PROJECT_NAME)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Platform: $$(uname -s)"
	@echo "Architecture: $$(uname -m)"
	@echo "Working directory: $$(pwd)"
	@echo "Virtual environment: $${VIRTUAL_ENV:-Not activated}"
	@echo ""
	@echo "Quick start:"
	@echo "  make setup     - Initial setup"
	@echo "  make test      - Run demo tests"
	@echo "  make test-all  - Run all tests"
	@echo "  make coverage  - Generate coverage report" 