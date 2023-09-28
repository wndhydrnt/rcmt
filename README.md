# rcmt

With rcmt you can

- create, modify or delete files across many repositories.
- merge global settings with user-configured settings in repositories.
- write your own tooling to manipulate files in repositories.

Take a look at the [documentation](https://rcmt.readthedocs.io/) to learn more.

## Development

### Set up virtualenv and install dependencies

Requirements:
- [poetry](https://python-poetry.org/)

```shell
poetry install --with docs
```

### Run linters

Requirements:
- [Set up virtualenv and install dependencies](#set-up-virtualenv-and-install-dependencies) (only once)

```shell
make lint
```

### Run tests

Requirements:
- [Set up virtualenv and install dependencies](#set-up-virtualenv-and-install-dependencies) (only once)

```shell
make test
```

### Generate and view docs

Requirements:
- [Set up virtualenv and install dependencies](#set-up-virtualenv-and-install-dependencies) (only once)

Start a local development server:

```shell
poetry run mkdocs serve
```

Open `http://127.0.0.1:8000/` in a browser.

### Create a new database migration

Requirements:
- [Set up virtualenv and install dependencies](#set-up-virtualenv-and-install-dependencies) (only once)

1. Ensure that the database is on the latest revision:
   ```shell
   poetry run alembic -c ./hack/alembic.ini upgrade head
   ```
2. Add, change or delete a model in [rcmt/database/\_\_init\_\_.py](./rcmt/database/__init__.py).
3. Let Alembic generate the new migration:
   ```shell
   poetry run alembic -c ./hack/alembic.ini revision --autogenerate -m 'Add model "Extension"'
   ```
   **Note:** Alembic cannot detect every change. Review the newly generated file in [rcmt/database/migrations/versions](./rcmt/database/migrations/versions).
   See [What does Autogenerate Detect (and what does it not detect?)](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)
   section in the documentation of Alembic for more details.
