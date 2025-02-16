# Contributing to Promptpal

We love your input! We want to make contributing to Promptpal as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints (using `ruff`).
6. Issue that pull request!

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/promptpal.git
   cd promptpal
   ```

2. Set up using Docker:
   ```bash
   # Build development image
   docker build --target development -t promptpal-dev .
   
   # Run development container
   docker run -it --rm -v $(pwd):/app promptpal-dev
   ```

   Or set up locally:
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate  # Windows
   
   # Install dependencies
   pip install -e ".[dev]"
   ```

3. Create a `.env` file:
   ```bash
   cp .env.template .env
   # Add your API keys
   ```

## Running Tests

```bash
# Using Docker
docker build --target testing -t promptpal-test .
docker run --rm promptpal-test

# Or locally
pytest tests/ -v --cov=promptpal
```

## Code Style

We use `ruff` for both linting and formatting. Before submitting a PR:

```bash
ruff check .
ruff format .
```

## License
By contributing, you agree that your contributions will be licensed under its MIT License. 