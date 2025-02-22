# syntax=docker/dockerfile:1

# Base stage with common dependencies
FROM python:3.11-slim AS base

WORKDIR /app

# Set uv environment variables
ENV UV_SYSTEM_PYTHON=1
ENV UV_LINK_MODE=copy

# Install system dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && chmod +x /usr/local/bin/uv

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY promptpal/ promptpal/
COPY tests/ tests/

# Development stage
FROM base AS development

# Install dependencies and set up environment
RUN uv pip install -e ".[dev]" && \
    useradd -m -s /bin/bash developer && \
    chown -R developer:developer /app

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER developer

# Command to run development server or shell
CMD ["bash"]

# Testing stage
FROM base AS testing

# Install dependencies and set up environment
RUN uv pip install -e ".[dev]" pytest && \
    useradd -m -s /bin/bash tester && \
    chown -R tester:tester /app

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER tester

# Command to run tests
CMD ["pytest", "tests/unit/", "-v", "-m", "not integration"] 