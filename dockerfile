# Etapa 1: Construcción de dependencias
FROM python:3.13-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app


# Instala curl y ca-certificates para HTTPS
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*
# Instalar dependencias del sistema para psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && gunicorn --version  # Verifica que gunicorn esté instalado

# Etapa 2: Imagen final para ejecución
FROM python:3.13-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Instalar bibliotecas necesarias para psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar gunicorn directamente en runtime como respaldo
RUN pip install gunicorn==21.2.0

RUN useradd --create-home appuser
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY . .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]