# syntax=docker/dockerfile:1
# Adapted from docker init; image references are recorded in infra/images.lock.json.
FROM ghcr.io/astral-sh/uv@sha256:b485bd65cc2cf1c9a93b3554012c9c3778cf7b1b5fd3d3096ce9e1226c97e1e6 AS uv
FROM python@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6 AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 ENVIRONMENT=production
WORKDIR /app

FROM base AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy
COPY pyproject.toml uv.lock .python-version ./
COPY apps/api/pyproject.toml apps/api/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev --all-packages

FROM base AS final
RUN adduser --disabled-password --gecos "" --no-create-home --uid 10001 appuser
COPY --from=build /app/.venv /app/.venv
COPY apps/api/src apps/api/src
COPY apps/api/alembic apps/api/alembic
COPY apps/api/alembic.ini apps/api/alembic.ini
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app/apps/api
USER appuser
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
