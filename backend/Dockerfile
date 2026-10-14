FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[dev]"
COPY . .
RUN chmod +x /app/scripts/entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/app/scripts/entrypoint.sh"]