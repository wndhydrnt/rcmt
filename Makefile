lint:
	black --check .
	mypy .
	isort --check-only .

test:
	pytest .

coverage:
	rm .coverage || true
	rm -rf ./htmlcov/
	coverage run --source=. --omit=.venv/*,tests/* -m pytest .
	coverage html
