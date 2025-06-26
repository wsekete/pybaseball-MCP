# Contributing to Pybaseball MCP Server

Thank you for your interest in contributing to the Pybaseball MCP Server! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

Before creating an issue, please check if it already exists. When creating a new issue:

1. **Use a clear and descriptive title**
2. **Provide detailed information:**
   - Steps to reproduce the problem
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)
   - Relevant log messages or error traces

3. **Use the appropriate issue template**

### Suggesting Features

We welcome feature suggestions! Please:

1. **Check if the feature already exists or is planned**
2. **Describe the feature clearly:**
   - What problem does it solve?
   - How would it work?
   - Who would benefit from it?

3. **Consider implementation complexity**
4. **Provide examples or mockups if applicable**

### Code Contributions

#### Getting Started

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/pybaseball-MCP.git
   cd pybaseball-MCP
   ```

3. **Set up the development environment:**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install pytest pytest-asyncio black isort flake8 mypy pre-commit
   
   # Set up pre-commit hooks
   pre-commit install
   ```

4. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Guidelines

##### Code Style

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run these before committing:
```bash
# Format code
black .
isort .

# Check linting
flake8 .

# Type checking
mypy .
```

##### Testing

- Write tests for new functionality
- Ensure existing tests pass
- Aim for good test coverage

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tools --cov=utils

# Run specific tests
pytest tests/test_player_tools.py
```

##### Documentation

- Update docstrings for new functions
- Add type hints
- Update README.md if needed
- Add examples for new features

#### Pull Request Process

1. **Ensure your code follows the style guidelines**
2. **Write or update tests as needed**
3. **Update documentation**
4. **Create a clear pull request:**
   - Descriptive title and description
   - Reference any related issues
   - Include screenshots for UI changes

5. **Ensure CI passes**
6. **Be responsive to feedback**

### Code Organization

#### Project Structure
```
pybaseball-mcp-server/
├── server.py              # Main MCP server
├── tools/                 # Tool implementations
│   ├── player_tools.py    # Player lookup tools
│   ├── stats_tools.py     # Statistics tools
│   └── plotting_tools.py  # Visualization tools
├── utils/                 # Shared utilities
│   ├── data_processing.py # Data formatting
│   └── validation.py      # Input validation
├── tests/                 # Test files
└── docs/                  # Documentation
```

#### Adding New Tools

To add a new tool:

1. **Choose the appropriate module** (or create a new one)
2. **Implement the tool function:**
   ```python
   @mcp.tool()
   def your_new_tool(
       param1: str,
       param2: int = 10,
       ctx: Context = None
   ) -> str:
       """
       Clear description of what the tool does.
       
       Args:
           param1: Description of parameter
           param2: Description with default value
           
       Returns:
           Description of return value
       """
       try:
           # Implementation here
           return "Success message"
       except Exception as e:
           logger.error(f"Error in your_new_tool: {e}")
           return f"❌ Error: {e}"
   ```

3. **Add input validation**
4. **Write tests**
5. **Update documentation**

#### Adding New Utilities

For shared functionality:

1. **Add to appropriate utility module**
2. **Write comprehensive docstrings**
3. **Include type hints**
4. **Write unit tests**

### Testing Guidelines

#### Test Categories

- **Unit tests**: Test individual functions
- **Integration tests**: Test tool interactions
- **Performance tests**: Test with large datasets

#### Writing Tests

```python
import pytest
from tools.player_tools import lookup_player_id

def test_lookup_player_valid():
    """Test player lookup with valid input"""
    result = lookup_player_id("Mike Trout")
    assert "Mike Trout" in result
    assert "❌" not in result

def test_lookup_player_invalid():
    """Test player lookup with invalid input"""
    result = lookup_player_id("NonexistentPlayer12345")
    assert "❌" in result

@pytest.mark.slow
def test_large_dataset():
    """Test with large dataset (marked as slow)"""
    # Test implementation
    pass
```

#### Test Data

- Use realistic but minimal test data
- Mock external API calls when possible
- Clean up test artifacts

### Documentation

#### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int = 10) -> str:
    """
    Brief description of the function.
    
    Longer description if needed. Explain the purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of parameter.
        param2: Description with default value.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When parameter is invalid.
        APIError: When external service fails.
        
    Example:
        >>> result = example_function("test", 5)
        >>> print(result)
        "Success"
    """
```

#### README Updates

When adding significant features:

1. Update the features list
2. Add usage examples
3. Update the tool reference table

### Release Process

#### Version Numbering

We use semantic versioning (SemVer):
- **Major** (X.0.0): Breaking changes
- **Minor** (1.X.0): New features (backward compatible)
- **Patch** (1.0.X): Bug fixes

#### Creating Releases

1. **Update version in pyproject.toml**
2. **Update CHANGELOG.md**
3. **Create release notes**
4. **Tag the release:**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

### Community Guidelines

#### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and improve
- Follow the project's code of conduct

#### Communication

- Use clear, descriptive language
- Be patient with newcomers
- Ask questions when unclear
- Share knowledge and help others

### Getting Help

If you need help:

1. **Check the documentation**
2. **Search existing issues**
3. **Ask in discussions**
4. **Contact maintainers**

### Recognition

Contributors will be recognized in:
- Release notes
- Contributors file
- Documentation

Thank you for contributing to the Pybaseball MCP Server! 🎾⚾
