# syntax=docker/dockerfile:1
# ---------- Stage 1: сборка зависимостей с uv ----------
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Кэширование слоя: зависимости пересобираются только при изменении pyproject/lock
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# ---------- Stage 2: минимальный рантайм ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app \
    && adduser --system --ingroup app app

WORKDIR /app

# Виртуальное окружение из builder-стадии (без исходников и кэша pip)
COPY --from=builder /app/.venv /app/.venv

COPY . .

RUN mkdir -p downloads logs data cookies \
    && chown -R app:app /app \
    && rm -f pyproject.toml uv.lock

USER app

CMD ["python", "main.py"]
