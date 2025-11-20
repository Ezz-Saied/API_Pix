FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for psycopg
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Pipfile for dependency installation
COPY Pipfile Pipfile.lock /app/

# Install pipenv and Python dependencies
RUN pip install --no-cache-dir pipenv
RUN pipenv install --system --deploy

# Copy the rest of the project
COPY . /app/

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "API.wsgi:application", "--bind", "0.0.0.0:8000"]
