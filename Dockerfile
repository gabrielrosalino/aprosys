FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libjpeg-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libopenjp2-7-dev \
        libtiff5-dev \
        tk-dev \
        libharfbuzz-dev \
        libfribidi-dev \
        libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* /app/

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir \
        "django>=5.2.3,<6.0.0" \
        "pillow>=11.2.1,<12.0.0" \
        "django-widget-tweaks>=1.5.0,<2.0.0"


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        zlib1g \
        libfreetype6 \
        liblcms2-2 \
        libopenjp2-7 \
        libtiff6 \
        libharfbuzz0b \
        libfribidi0 \
        libwebp7 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY . /app

EXPOSE 8000

CMD ["python", "aprosys/manage.py", "runserver", "0.0.0.0:8000"]
