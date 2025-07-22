# Audio Processing System - Testing Framework  
# Docker image for comprehensive testing

FROM python:3.11-slim

# Metadata
LABEL maintainer="Audio Processing Team"
LABEL description="Audio Processing System Testing Framework"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTEST_CURRENT_TEST=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for Linux
RUN apt-get update && apt-get install -y \
    # Build dependencies
    build-essential \
    gcc \
    g++ \
    make \
    # PostgreSQL client development libraries
    libpq-dev \
    postgresql-client \
    # Redis tools
    redis-tools \
    # Audio processing libraries (for future use)
    libsndfile1-dev \
    libasound2-dev \
    # Network and security tools
    curl \
    wget \
    net-tools \
    # Process monitoring
    htop \
    procps \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create application directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY pytest/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x scripts/*.sh

# Create necessary directories
RUN mkdir -p logs test-reports performance_results coverage_html

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash tester && \
    chown -R tester:tester /app

# Switch to non-root user
USER tester

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python pytest/demo_test.py > /dev/null 2>&1 || exit 1

# Default command - run all tests
CMD ["./scripts/run_tests.sh", "all", "--parallel"]

# Expose any ports if needed for monitoring
EXPOSE 8080

# Volume for test results
VOLUME ["/app/test-reports", "/app/coverage_html", "/app/logs"] 