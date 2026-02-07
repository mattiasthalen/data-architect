.DEFAULT_GOAL := check

.PHONY: bootstrap lint format type test check clean

bootstrap:  ## Install deps + git hooks
	uv sync --dev
	@echo "Installing git hooks..."
	@cp scripts/hooks/pre-commit .git/hooks/pre-commit
	@cp scripts/hooks/commit-msg .git/hooks/commit-msg
	@chmod +x .git/hooks/pre-commit .git/hooks/commit-msg
	@echo "Done! Git hooks installed."

lint:  ## Run linter and formatter check
	uv run ruff check .
	uv run ruff format --check .

format:  ## Auto-fix lint issues and format
	uv run ruff check --fix .
	uv run ruff format .

type:  ## Run type checker
	uv run mypy src

test:  ## Run tests with coverage
	uv run pytest

check: lint type test  ## Run all checks (lint + type + test)

clean:  ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info .mypy_cache .pytest_cache .coverage htmlcov/ .ruff_cache
