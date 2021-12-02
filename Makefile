RCMT_VERSION ?= develop

lint:
	poetry run black --check .
	poetry run mypy --exclude 'docs/examples/.+\.py' .
	poetry run isort --check-only .

test:
	poetry run pytest .

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

docker_push:
	docker push wandhydrant/rcmt:$(RCMT_VERSION)
