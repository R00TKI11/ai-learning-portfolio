# Contributing to AI Log Triage Agent

Thank you for considering contributing to the AI Log Triage Agent! This document provides guidelines for contributing to this project.

## Code of Conduct

Be respectful and constructive in all interactions. We aim to create a welcoming environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please open an issue with:
- A clear description of the enhancement
- Use cases and benefits
- Any potential drawbacks or considerations

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding standards below
3. **Add tests** for any new functionality
4. **Ensure all tests pass**: `python -m unittest discover -s tests`
5. **Update documentation** as needed (README, docstrings, etc.)
6. **Commit your changes** with clear, descriptive commit messages
7. **Push to your fork** and submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/R00TKI11/ai-learning-portfolio.git
cd ai-learning-portfolio/projects/ai-log-triage-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in editable mode with dev dependencies
pip install -e .
pip install pytest black flake8  # optional dev tools

# Run tests
python -m unittest discover -s tests -v
```

## Coding Standards

### Python Style
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Keep functions focused and concise
- Maximum line length: 100 characters (flexible for readability)

### Documentation
- All modules should have docstrings
- All public functions/classes should have docstrings
- Use type hints where appropriate
- Update README.md for user-facing changes

### Testing
- Write unit tests for new functionality
- Maintain or improve test coverage
- Test files should mirror the structure of source files
- Use descriptive test names: `test_feature_when_condition_then_expected`

### Commits
- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep commits focused on a single change
- Reference issues when applicable: "Fix #123: Description"

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

All source files should include the SPDX license identifier:

```python
"""
Module description

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""
```

## Questions?

Feel free to open an issue for any questions about contributing!
