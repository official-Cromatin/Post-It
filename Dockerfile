# Base image (multi-arch via buildx)
FROM python:3.10-slim

# Prevents pyc files + enables unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files (via .dockerignore)
COPY . .

# Create non-root user
RUN adduser --disabled-password --no-create-home --gecos "" appuser \
    && chown -R appuser /app
USER appuser

# Default command
ENTRYPOINT ["python", "src/main.py"]
