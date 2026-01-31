# Multi-stage Dockerfile for ExFrame - Expertise Framework

# Stage 1: Builder - Install dependencies
FROM python:3.13-slim AS builder

# Set working directory
WORKDIR /build

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Pre-install CPU-only PyTorch (much smaller, no CUDA dependencies)
# Then install remaining requirements
RUN pip install --no-cache-dir --user torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime - Final minimal image
FROM python:3.13-slim

# Set labels
LABEL maintainer="ExFrame Contributors"
LABEL description="ExFrame - Domain-agnostic AI-powered knowledge management system"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_HOME=/app \
    PYTHONPATH=/app:$PYTHONPATH

# Create a non-root user with configurable UID (defaults to 1000 = first user on most systems)
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd -g $USER_GID appuser && \
    useradd -u $USER_UID -g $USER_GID appuser

# Set working directory
WORKDIR $APP_HOME

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder to a shared location
COPY --from=builder /root/.local /usr/local

# Make sure scripts are accessible
ENV PATH=/usr/local/bin:$PATH

# Copy application code (includes the frontend/index.html)
COPY generic_framework/ $APP_HOME/
COPY expertise_scanner/ $APP_HOME/expertise_scanner/

# Create necessary directories with proper permissions
RUN mkdir -p $APP_HOME/data \
    $APP_HOME/logs \
    $APP_HOME/expertise_scanner/data/patterns \
    $APP_HOME/expertise_scanner/data/history && \
    chown -R appuser:appuser $APP_HOME

# Copy entrypoint script and set permissions
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set entrypoint (runs as root to fix permissions, then switches to appuser)
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Expose the application port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Run the application
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "3000"]
