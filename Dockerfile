# BSEE - Binary Structure Exploration Engine Dockerfile
# Multi-stage build for production deployment

# Build stage
FROM python:3.9-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Set labels
LABEL maintainer="BSEE Team <support@bsee.dev>" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="BSEE" \
      org.label-schema.description="Binary Structure Exploration Engine" \
      org.label-schema.url="https://github.com/bsee/bsee" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/bsee/bsee.git" \
      org.label-schema.vendor="BSEE" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libmagic1 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-dev.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Production stage
FROM python:3.9-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    BSEE_CONFIG_PATH="/app/config/production.yaml" \
    BSEE_LOG_LEVEL="INFO"

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r bsee && useradd -r -g bsee bsee

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create application directories
WORKDIR /app
RUN mkdir -p /app/config /app/logs /app/data /app/cache && \
    chown -R bsee:bsee /app

# Copy application code
COPY --chown=bsee:bsee . /app/

# Install application in development mode
RUN pip install -e .

# Switch to non-root user
USER bsee

# Create necessary directories
RUN mkdir -p /app/logs /app/cache /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 8080

# Default command
CMD ["uvicorn", "bsee.api.server:app", "--host", "0.0.0.0", "--port", "8000"]

# Development variant
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN pip install -r requirements-dev.txt

# Install additional development tools
RUN apt-get update && apt-get install -y \
    vim \
    nano \
    htop \
    strace \
    && rm -rf /var/lib/apt/lists/*

# Switch to bsee user
USER bsee

# Override command for development
CMD ["uvicorn", "bsee.api.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]