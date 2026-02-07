.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap:  ## Install deps + git hooks
	uv sync --dev
	@echo "Installing git hooks..."
	@cp scripts/hooks/pre-commit .git/hooks/pre-commit
	@cp scripts/hooks/commit-msg .git/hooks/commit-msg
	@chmod +x .git/hooks/pre-commit .git/hooks/commit-msg
	@echo "Done! Git hooks installed."

.PHONY: lint
lint:  ## Run linter and formatter check
	uv run ruff check .
	uv run ruff format --check .

.PHONY: format
format:  ## Auto-fix lint issues and format
	uv run ruff check --fix .
	uv run ruff format .

.PHONY: type
type:  ## Run type checker
	uv run mypy src

.PHONY: test
test:  ## Run tests with coverage
	uv run pytest

.PHONY: check
check: lint type test  ## Run all checks (lint + type + test)

.PHONY: clean
clean:  ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info .mypy_cache .pytest_cache .coverage htmlcov/ .ruff_cache
