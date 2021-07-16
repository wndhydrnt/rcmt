lint:
	black --check .
	mypy .
	isort --check-only .

test:
	pytest .

coverage:
	rm .coverage || true
	rm -rf ./htmlcov/
	coverage run
	coverage html
