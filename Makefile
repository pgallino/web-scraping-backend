# Makefile reorganizado y minimalista
# Objetivo: dejar comandos claros y pocos atajos para desarrollo y deploy.

# Variables
PYTHON_FILES = src

default: help

.PHONY: help format format-check lint check test test-unit test-acceptance migrate ci

# Ayuda: lista los comandos recomendados
help:
	@echo "Comandos principales:"
	@echo "  make format        # Formatea el código (black/isort)"
	@echo "  make check         # Formatea y chequea tipos (format + lint)"
	@echo "  make test          # Ejecuta tests (unit + acceptance)"
	@echo "  make ci            # Ejecuta checks y tests (útil en CI)"
	@echo "\n(Nota: hay targets host-level como dev-up/dev-down que pueden usarse opcionalmente.)"


# -----------------------------
# Formatting / linting / tests
# -----------------------------

format:
	@echo "-> Formateando código con black e isort..."
	isort $(PYTHON_FILES)
	black $(PYTHON_FILES)

format-check:
	@echo "-> Verificando formato..."
	isort --check-only $(PYTHON_FILES)
	black --check $(PYTHON_FILES)

lint:
	@echo "-> Chequeo de tipos (mypy)..."
	mypy $(PYTHON_FILES)


# Comando de conveniencia: corre format + lint
check: format-check lint
	@echo "-> check: formato y lint completados"

# Tests
test: test-unit test-acceptance
	@echo "-> Tests completos ejecutados"

test-unit:
	@echo "-> Ejecutando tests unitarios..."
	pytest --cov=src/domain --cov=src/adapters \
		--cov-report=html:coverage-unit-html \
		--cov-report=term-missing \
		--cov-fail-under=75 --cov-config=.coveragerc tests/unit

test-acceptance:
	@echo "-> Ejecutando tests de aceptación (BDD)..."
	# Generate HTML coverage report for acceptance tests
	pytest --cov=src --cov-report=html:coverage-acceptance-html tests/acceptance


test-integration:
	@echo "-> Ejecutando tests de integración..."
	pytest --cov=src --cov-report=html:coverage-integration-html tests/integration

# -----------------------------
# Migrations
# -----------------------------

# Upgrade DB schema (host)
alembic-upgrade:
	PYTHONPATH=$(shell pwd) alembic upgrade head

# Shortcut: run migrations inside dev container (recommended for dev)
# This target is useful when you want to run the upgrade from inside the
# development container (keeps the same behaviour as before).
migrate:
	@echo "-> Ejecutando migraciones (dentro del contenedor dev)"
	PYTHONPATH=$(shell pwd) alembic upgrade head

# -----------------------------
# CI convenience
# -----------------------------

ci: format-check lint test
	@echo "✅ CI OK"


