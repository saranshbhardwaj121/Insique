FROM python:3.12-slim@sha256:2ca4b2e6d0f05e4a9244b2d26c75e2856d0e09f99d39441f3f3c7b0e6e2e7f60

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN adduser --disabled-password --gecos "" --uid 1000 appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY backend/ backend/

RUN pip install --no-cache-dir .

USER appuser

EXPOSE 8000/tcp

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
