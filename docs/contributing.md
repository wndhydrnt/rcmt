# Contributing

This page details how to contribute to the
[core rcmt repository](https://github.com/wndhydrnt/rcmt).

## Set up poetry

Requirements:

- [poetry](https://python-poetry.org/)

```shell
poetry install --with docs
```

## Run linters

Requirements:

- [Set up virtualenv and install dependencies](#set-up-poetry) (only once)

```shell
make lint
```

## Run tests

Requirements:

- [Set up virtualenv and install dependencies](#set-up-poetry) (only once)

```shell
make test
```

## Generate and view docs

Requirements:

- [Set up virtualenv and install dependencies](#set-up-poetry) (only once)

Start a local development server:

```shell
poetry run mkdocs serve
```

Open `http://127.0.0.1:8000/` in a browser.

## Create a new database migration

Requirements:

- [Set up virtualenv and install dependencies](#set-up-poetry) (only once)

1. Ensure that the database is on the latest revision:
   ```shell
   poetry run alembic -c ./hack/alembic.ini upgrade head
   ```
2. Add, change or delete a model in [rcmt/database/\_\_init\_\_.py](https://github.com/wndhydrnt/rcmt/rcmt/database/__init__.py).
3. Let Alembic generate the new migration:
   ```shell
   poetry run alembic -c ./hack/alembic.ini revision --autogenerate -m 'Add model "Extension"'
   ```
   **Note:** Alembic cannot detect every change. Review the newly generated file in [rcmt/database/migrations/versions](https://github.com/wndhydrnt/rcmt/rcmt/database/migrations/versions).
   See [What does Autogenerate Detect (and what does it not detect?)](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)
   section in the documentation of Alembic for more details.
