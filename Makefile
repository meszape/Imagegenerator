.PHONY: install test run lint
install:
	python -m pip install -e '.[dev]'
test:
	pytest -q
run:
	uvicorn app.main:app --reload
lint:
	ruff check src tests
