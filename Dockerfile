FROM python:3.10.6 as build
WORKDIR /opt
RUN pip install --no-cache-dir poetry
COPY poetry.lock pyproject.toml README.md ./
COPY ./rcmt ./rcmt
RUN poetry build

FROM python:3.10.6
RUN apt-get update \
    && apt-get install --no-install-recommends -y git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /opt/dist/rcmt-*.whl /
RUN pip install /rcmt-*.whl \
    && rm /rcmt-*.whl \
    && useradd -ms /bin/bash rcmt
USER rcmt
WORKDIR /home/rcmt
ENTRYPOINT ["rcmt"]
