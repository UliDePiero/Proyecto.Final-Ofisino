FROM python:3.9.6-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=120 \
    POETRY_VERSION=1.1.6 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev \
    nano \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Install dependencies
COPY requirements_dev.txt requirements.txt /code/
RUN pip install -r requirements_dev.txt

# Copy everything else
COPY . /code

# Read desired port for environment, or default to 8000
ENV APP_PORT=${APP_PORT:-8000}

# Start app
CMD gunicorn --bind 0.0.0.0:$APP_PORT app.api:create_app\(\) --reload --access-logfile -
