FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

FROM base AS runtime

ENV DEFAULT_PHONE="" \
    DEFAULT_TOKEN="" \
    DEBUG="false"

ENTRYPOINT ["tele2-trade"]