# Multi-stage build for minimal image size
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage - minimal runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 mem0user && \
    chown -R mem0user:mem0user /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/mem0user/.local

# Copy application code
COPY --chown=mem0user:mem0user . .

# Switch to non-root user
USER mem0user

# Add local Python packages to PATH
ENV PATH=/home/mem0user/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "mem0_api:app", "--host", "0.0.0.0", "--port", "8000"]
