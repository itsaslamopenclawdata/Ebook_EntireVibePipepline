# Multi-stage build for Vibe PDF Backend
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    LaTeX \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-xetex \
    latexmk \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
FROM base as builder

RUN pip install --upgrade pip setuptools wheel

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM base as production

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appgroup backend/app ./app
COPY --chown=appuser:appgroup backend/requirements.txt .

# Set PATH to include user Python packages
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONPATH=/app

# Expose ports
EXPOSE 8000 5555

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run as non-root user
USER appuser

# Run Celery worker
CMD ["sh", "-c", "celery -A app.worker worker --loglevel=info --concurrency=4"]

# Alternative: Run FastAPI server
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
