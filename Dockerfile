FROM python:3.10-slim as build

RUN mkdir -p /opt/poetry
ENV POETRY_HOME=/opt/poetry

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python -

COPY . ./
RUN ${POETRY_HOME}/bin/poetry export --without-hashes -o requirements.txt
RUN ${POETRY_HOME}/bin/poetry build

FROM python:3.10-slim

WORKDIR /install

COPY --from=build dist/*.whl requirements.txt ./
RUN pip install --no-cache-dir --no-compile -r requirements.txt *.whl

WORKDIR /app

ENTRYPOINT ["pointing-offset"]
