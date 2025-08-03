# Multi-stage build for optimized production image
FROM python:3.13-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    libopencv-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files and README for package build
COPY pyproject.toml uv.lock README.md ./
COPY src/ /app/src/

# Install dependencies and the package itself
RUN uv sync --frozen --no-cache && \
    uv pip install -e .

# Production stage
FROM python:3.13-slim AS production

# Install runtime dependencies (minimal opencv dependencies)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r qrreader && useradd -r -g qrreader qrreader

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=qrreader:qrreader src/ /app/src/
COPY --chown=qrreader:qrreader pyproject.toml /app/

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER qrreader

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import qr_code_reader; print('OK')" || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "qr_code_reader.server"]