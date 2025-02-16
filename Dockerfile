# syntax=docker/dockerfile:1

# Base stage with common dependencies
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency installation
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY promptpal/ promptpal/
COPY tests/ tests/

# Development stage
FROM base as development

# Install development dependencies
RUN uv pip install -e ".[dev]"

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN useradd -m -s /bin/bash developer
RUN chown -R developer:developer /app
USER developer

# Command to run development server or shell
CMD ["bash"]

# Testing stage
FROM base as testing

# Install test dependencies
RUN uv pip install -e ".[dev]" pytest-cov

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GEMINI_API_KEY="test_key"

# Create coverage directory
RUN mkdir coverage && chmod 777 coverage

# Create a non-root user
RUN useradd -m -s /bin/bash tester
RUN chown -R tester:tester /app
USER tester

# Command to run tests
CMD ["pytest", "tests/", "-v", "--cov=promptpal", "--cov-report=term-missing"] 