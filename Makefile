lint:
	black --check .
	mypy .
	isort --check-only .

test:
	pytest .
