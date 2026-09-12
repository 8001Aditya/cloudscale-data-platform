FROM python:3.11.13-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CLOUDSCALE_ENVIRONMENT=local
ENV CLOUDSCALE_LOG_LEVEL=INFO
ENV CLOUDSCALE_EVENT_SCHEMA_VERSION=1

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --disable-pip-version-check --no-cache-dir --upgrade pip \
    && python -m pip install --disable-pip-version-check --no-cache-dir . \
    && addgroup --system cloudscale \
    && adduser --system --ingroup cloudscale cloudscale \
    && mkdir -p /app/data \
    && chown -R cloudscale:cloudscale /app

USER cloudscale

ENTRYPOINT ["cloudscale-produce-orders"]
