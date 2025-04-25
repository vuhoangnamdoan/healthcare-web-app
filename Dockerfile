FROM python:3.10-slim as base

# Setup environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Create and set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Production specific configuration
FROM base as production

# Create non-root user for security
RUN useradd -m -s /bin/bash app && \
    chown -R app:app /app
USER app

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "health_system.wsgi:application"]

# Development specific configuration
FROM base as development

# Install development dependencies
RUN pip install pytest-watch ipython django-debug-toolbar

# Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]