FROM python:3.12-slim-bookworm
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1 \
UV_LINK_MODE=copy \
UV_PYTHON_DOWNLOADS=never \
UV_PROJECT_ENVIRONMENT=/app/.venv
RUN groupadd -r django && useradd -r -m -g django django_user
COPY . .
RUN mkdir -p /app/staticfiles /app/mediafiles
RUN chown -R django_user:django /app/staticfiles /app/mediafiles
RUN chown -R django_user:django /app
RUN chmod +x /app/entrypoint.sh
USER django_user
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "social_scheduler.wsgi:application"]