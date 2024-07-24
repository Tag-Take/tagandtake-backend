# Define the base image for common settings
FROM python:3.11-slim as base

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    PATH="/root/.local/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    postgresql-client \ 
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the Python dependencies file
COPY pyproject.toml poetry.lock* /app/

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Dev image
FROM base as development
COPY . /app/
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

# Prod image
FROM base as production
COPY . /app/
CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8000", "tagandtake.wsgi:application"]