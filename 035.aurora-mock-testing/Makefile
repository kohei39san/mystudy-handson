# Aurora Mock Testing Project Makefile

.PHONY: help install test lint format deploy clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run unit tests"
	@echo "  lint       - Run code linting"
	@echo "  format     - Format code with black"
	@echo "  deploy     - Deploy infrastructure"
	@echo "  clean      - Clean up temporary files"

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	pytest tests/ -v

# Run specific test classes
test-unit:
	pytest tests/ -v -m unit

test-integration:
	pytest tests/ -v -m integration

# Code linting
lint:
	flake8 scripts/ tests/
	mypy scripts/ --ignore-missing-imports

# Code formatting
format:
	black scripts/ tests/

# Deploy infrastructure
deploy:
	chmod +x scripts/deploy.sh
	./scripts/deploy.sh

# Terraform operations
tf-init:
	terraform init

tf-plan:
	terraform plan -var="project_name=aurora-mock-testing" -var="environment=dev"

tf-apply:
	terraform apply -var="project_name=aurora-mock-testing" -var="environment=dev" -auto-approve

tf-destroy:
	terraform destroy -var="project_name=aurora-mock-testing" -var="environment=dev" -auto-approve

# CloudFormation operations
cfn-validate:
	aws cloudformation validate-template --template-body file://cfn/aurora.yaml
	aws cloudformation validate-template --template-body file://cfn/secrets-manager.yaml
	aws cloudformation validate-template --template-body file://cfn/ecs.yaml
	aws cloudformation validate-template --template-body file://cfn/lambda.yaml

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf .mypy_cache/