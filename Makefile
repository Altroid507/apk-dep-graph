.PHONY: run test lint clean

PYTHON ?= python3
export PYTHONPATH := src

run:
	$(PYTHON) -m src --config config.example.csv

test:
	$(PYTHON) -m pytest -q

lint:
	ruff check src tests

clean:
	rm -rf .pytest_cache __pycache__ src/__pycache__