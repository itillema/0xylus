# Run recipes with `uv run just <recipe>` so the project's tools are on PATH.

[windows]
set shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# List the recipes.
default:
    @just --list

# Lint, check formatting, type-check and run the unit tests.
check: lint format-check typecheck test

# Lint with ruff.
lint:
    ruff check

# Check formatting without changing files.
format-check:
    ruff format --check

# Format the code and apply safe lint fixes.
fmt:
    ruff format
    ruff check --fix

# Type-check with mypy (strict).
typecheck:
    mypy

# Run the unit tests.
test:
    pytest -q -m 'not integration'

# Run the integration tests.
integration:
    pytest -q -m integration
