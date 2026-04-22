# AGENTS.md

This is a Python library for parsing RPM spec files.

Make sure to run commands in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run tests:

```bash
pytest                    # Run all tests
pytest --cov=pyrpm.spec   # Run tests with coverage
pytest tests/test_spec_file_parser.py -k test_name  # Run single test
```

Type checking:

```bash
mypy .  # Run type checker (strict mode enabled)
```

Linting:

```bash
pylint --rcfile=.pylintrc pyrpm  # Run linter on main module
```

Code formatting:

```bash
black --line-length 130 .  # Format code (line length: 130)
```

Build and release:

```bash
flit build   # Build distribution
flit publish # Publish to PyPI
```

