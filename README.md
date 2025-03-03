# PromptPal

Python based tool for improved LLM interactions using the Google Gemini API.

[![Tests](https://github.com/mattjenior/promptpal/actions/workflows/test.yml/badge.svg)](https://github.com/mattjenior/promptpal/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/mattjenior/promptpal/branch/main/graph/badge.svg)](https://codecov.io/gh/mattjenior/promptpal)
[![PyPI version](https://badge.fury.io/py/promptpal.svg)](https://badge.fury.io/py/promptpal)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This package is a Python-based prompt enhancing tool that allows users to automate significant portions of interactions with the Google Gemini API. It provides several powerful features, including automated system role selection, prompt refinement, iterative response parsing, and the ability to save identified code snippets as separate scripts. Additionally, it includes basic chain of thought enforcement in prompts and associative glyph representation in prompts.

## Requirements
- Python >= 3.11
- google-genai >= 1.2.0
- Other dependencies listed in pyproject.toml

## Key Features

- **Automated System Role Selection**: Automatically assign system roles for your LLM interaction, optimizing the model's responses based on your desired use case 
- **Chain of Thought Enforcement**: Adds prompts that track reasoning and thought process, improving responses in scenarios requiring step-by-step reasoning
- **Automated Prompt Refinement and Glyph Representation**: Will automatically refactor prompts to be more descriptive and structured for improved LLM interpretability
- **Flexible Parameterization**: Simple, yet powerful, arguments during agent initialization allow easy interaction with the Gemini API
- **Code Detection**: The tool automatically identifies code snippets in the responses from the model, formats them properly, saves as separate script files for future use or execution
- **File and Directory Structure Comprehension**: Understands and reads in content of files listed directly in the prompt, and is also able to recursively read in entire subdirectories

## Table of Contents

1. [Installation](#installation)
2. [Development Setup](#development-setup)
3. [Usage](#usage)
4. [Testing](#testing)
5. [Contributing](#contributing)
6. [License](#license)

## Installation

### Using pip
```bash
pip install promptpal
```

### From source
```bash
git clone https://github.com/mattjenior/promptpal.git
cd promptpal
pip install -e .
```

### API Keys
Before using the tool, you need to set up your Google Gemini API key. The package reads it from the environment variable `GEMINI_API_KEY`.

```bash
export GEMINI_API_KEY="your_gemini_api_key"
```

## Development Setup

We use `uv` for dependency management and virtual environment creation. Here's how to set up your development environment:

1. **Install uv**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Create virtual environment and install dependencies**:
```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

uv pip install -e ".[dev]"
```

3. **Using Docker for development**:
```bash
# Build development image
docker build --target development -t promptpal-dev .

# Run development container
docker run -it --rm -v $(pwd):/app promptpal-dev
```

## Testing

We use pytest for testing. Tests are organized into unit and integration tests.

### Running tests locally:
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=promptpal --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_promptpal.py -v
```

### Running tests with Docker:
```bash
# Build test image
docker build --target testing -t promptpal-test .

# Run tests
docker run --rm promptpal-test
```

### Code Style
We use `ruff` for both linting and formatting:
```bash
# Check code
ruff check .

# Format code
ruff format .
```

## Usage

### Basic Usage

```python
from promptpal.promptpal import Promptpal

# Set up output directory for generated files
output_dir = "./example_output"

# Initialize Promptpal with default roles
promptpal = Promptpal(load_default_roles=True, output_dir=output_dir)

# List available roles
print("Available Roles:")
for role_name in promptpal.list_roles():
    print(f"- {role_name}")

# Use analyst role for content generation
response = promptpal.chat(
    "analyst", 
    "Analyze the gene expression data for patterns."
)
print(response)

# Refine a prompt using keyword refinement
refined_prompt = promptpal.refine_prompt(
    "Explain the process of DNA replication.",
    keyword_refinement="simplify"
)
print("Refined Prompt:", refined_prompt)

# Reset chat for a new session
promptpal.new_chat()

# Generate and save code snippets
response = promptpal.chat(
    "developer",
    "Write a Python function to calculate the GC content of a DNA sequence.",
    write_code=True
)

# Generate images
response = promptpal.chat(
    "artist",
    "Create a detailed and artistic representation of a DNA double helix."
)
```

### Configuration Options

The `Promptpal` class accepts the following parameters:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `load_default_roles` | bool | Load predefined roles from roles.yaml | `True` |
| `output_dir` | str | Directory for saving generated files | `"./generated_files"` |
| `model` | str | Gemini model to use | `"gemini-2.0-flash-001"` |
| `temperature` | float | Model temperature (0.0 to 2.0) | `0.7` |
| `top_p` | float | Top-p sampling parameter | `0.8` |
| `top_k` | int | Top-k sampling parameter | `40` |
| `max_output_tokens` | int | Maximum output length | `2048` |

### Available Roles

- **analyst**: Data analysis and interpretation
- **artist**: Image generation and creative tasks
- **developer**: Code generation and software development
- **prompt**: Prompt engineering and optimization
- **tester**: Test case generation and QA
- **writer**: Content creation and documentation
- **editor**: Text editing and refinement

### Working with Files

```python
# Save generated code to files
promptpal.chat(
    "developer",
    "Write a unit test for a string reversal function",
    write_code=True
)

# Process files in prompt
promptpal.chat(
    "analyst",
    "Analyze the contents of /path/to/data.csv"
)
```

## Interactive Prompt Refinement

PromptPal includes an interactive prompt refinement feature that allows you to iteratively improve your prompts:

```python
from promptpal import Promptpal

# Initialize PromptPal
pal = Promptpal()

# Start with an initial prompt
initial_prompt = "Create a data visualization of climate change trends."

# Refine the prompt interactively
refined_prompt = pal.interactive_prompt_refinement(initial_prompt)

# Use the refined prompt
response = pal.chat("assistant", refined_prompt)
```

The interactive refinement process offers:

- Different refinement techniques (glyph, chain of thought, keyword)
- LLM feedback on your prompts
- Version history tracking
- The ability to revert to previous versions

For more details, see the [Interactive Prompt Refinement Documentation](docs/interactive_prompt_refinement.md).

## Adding Custom Roles

```python
from promptpal import Promptpal
from promptpal.roles import Role

# Initialize PromptPal
pal = Promptpal()

# Create a custom role
data_scientist = Role(
    name="data_scientist",
    description="Expertise in data analysis and visualization",
    system_instruction="You are a data scientist with expertise in analyzing and visualizing data.",
    temperature=0.2,
)

# Add the role
pal.add_roles([data_scientist])

# Use the custom role
response = pal.chat("data_scientist", "How would you analyze this dataset?")
```

## Advanced Features

### Prompt Refinement

```python
from promptpal import Promptpal

pal = Promptpal()

# Original prompt
original_prompt = "Write a poem about the ocean."

# Refine using glyph refinement
glyph_refined = pal.refine_prompt(original_prompt, glyph_refinement=True)

# Refine using chain of thought
cot_refined = pal.refine_prompt(original_prompt, chain_of_thought=True)

# Refine using keyword refinement
keyword_refined = pal.refine_prompt(original_prompt, keyword_refinement="elaborate")
```

### Chat Statistics

```python
from promptpal import Promptpal

pal = Promptpal()

# Have some conversations
pal.chat("assistant", "Hello, how are you?")
pal.chat("creativity", "Give me ideas for a novel.")

# Get statistics
stats = pal.get_chat_stats()
print(f"Tokens used: {stats['tokens_used']}")
print(f"Messages sent: {stats['messages_sent']}")
print(f"Files written: {stats['files_written']}")
print(f"Messages per role: {stats['messages_per_role']}")
```

## Continuous Integration and Deployment

### CI Pipeline

Our GitHub Actions workflow (`test.yml`) automatically runs on every push and pull request:

1. **Linting**: Checks code style with ruff
2. **Testing**: Runs unit tests with pytest
3. **Coverage**: Reports test coverage to Codecov

```yaml
# Trigger CI on push or pull request
on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint with ruff
        run: |
          ruff check .
          ruff format --check .

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          docker build --target testing -t promptpal-test .
          docker run --rm promptpal-test
```

### Creating a Release

1. **Update Version**:
   - Create a new branch: `git checkout -b release/vX.Y.Z`
   - Update version in `pyproject.toml`
   - Update CHANGELOG.md
   - Commit changes: `git commit -m "Bump version to X.Y.Z"`

2. **Create Pull Request**:
   - Push branch and create PR to main
   - Ensure all tests pass
   - Get review approval

3. **Publish Release**:
   - Merge PR to main
   - Go to GitHub Actions
   - Select "Publish to PyPI" workflow
   - Click "Run workflow"
   - Enter version number (e.g., "1.4.0")

The publish workflow will:
- Build the package
- Publish to PyPI
- Create a Git tag
- Create a GitHub release

### Release Checklist

- [ ] Update version in pyproject.toml
- [ ] Update CHANGELOG.md
- [ ] Update documentation if needed
- [ ] Run tests locally
- [ ] Create and merge PR
- [ ] Trigger publish workflow
- [ ] Verify PyPI package
- [ ] Verify documentation updates

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Development Process
1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Make your changes
5. Run tests and ensure they pass
6. Submit a pull request

## Security

Please read [SECURITY.md](SECURITY.md) for details on our security policy and how to report security vulnerabilities.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.
