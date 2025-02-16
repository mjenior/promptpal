# syntax=docker/dockerfile:1

# Base stage with common dependencies
FROM ghcr.io/astral-sh/uv:0.6.0-python3.11-slim AS base

WORKDIR /app

# Set uv environment variables
ENV UV_SYSTEM_PYTHON=1
ENV UV_LINK_MODE=copy

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    && rm -rf /var/lib/apt/lists/*

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
RUN uv pip install -e ".[dev]" pytest-cov && \
    mkdir coverage && \
    chmod 777 coverage && \
    useradd -m -s /bin/bash tester && \
    chown -R tester:tester /app

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER tester

# Command to run tests
CMD ["pytest", "tests/unit/", "-v", "--cov=promptpal", "--cov-report=term-missing"] 