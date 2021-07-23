FROM python:3.9-slim as build
RUN apt-get update && apt-get install -y git
WORKDIR /opt
RUN pip install poetry
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml README.md ./
COPY rcmt rcmt
RUN poetry install --no-dev --no-interaction --no-ansi
RUN pip uninstall -y poetry
ENTRYPOINT ["rcmt"]
