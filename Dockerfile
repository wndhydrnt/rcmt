FROM python:3.9-slim as build
RUN apt-get update \
    && apt-get install --no-install-recommends -y git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml README.md ./
COPY rcmt rcmt
RUN poetry install --no-dev --no-interaction --no-ansi \
    && pip uninstall -y poetry \
    && useradd -ms /bin/bash rcmt
USER rcmt
WORKDIR /home/rcmt
CMD ["rcmt"]
