RCMT_VERSION ?= develop

lint:
	poetry run black --check .
	poetry run mypy --exclude '(docs/examples/|tests/fixtures/).+\.py' .
	find ./docs/examples -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 -n1 poetry run mypy
	poetry run isort --check-only .
	poetry run flake8 --extend-ignore E501 ./rcmt ./docs/examples

test:
	poetry run pytest .

test_debug:
	poetry run pytest -rP .

coverage:
	rm .coverage || true
	rm -rf ./htmlcov/
	poetry run coverage run
	poetry run coverage html

publish:
	@poetry publish --build --username $(PUBLISH_USERNAME) --password $(PUBLISH_PASSWORD)

.PHONY: docs
docs:
	cd docs/ && poetry run make html

docker_build:
	docker build -t wandhydrant/rcmt:$(RCMT_VERSION) .

docker_build_all_platforms:
	docker buildx build --platform linux/amd64,linux/arm64 -t wandhydrant/rcmt:$(RCMT_VERSION) .

docker_push:
	docker buildx build --push --platform linux/amd64,linux/arm64 -t wandhydrant/rcmt:$(RCMT_VERSION) .
