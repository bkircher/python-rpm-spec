# AGENTS.md

## Project Overview

python-rpm-spec is a Python library for parsing RPM spec files without requiring
`/usr/bin/rpm` or any RPM tools. It provides read-only access to spec file
contents and supports all platforms including Windows.

The library uses regex-based parsing to extract information from RPM spec files.
While not complete, it handles the most common spec file elements.

## Key Commands

### Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Testing

```bash
pytest                    # Run all tests
pytest --cov=pyrpm.spec   # Run tests with coverage
pytest tests/test_spec_file_parser.py -k test_name  # Run single test
```

### Type Checking

```bash
mypy .  # Run type checker (strict mode enabled)
```

### Linting

```bash
pylint --rcfile=.pylintrc pyrpm  # Run linter on main module
```

### Code Formatting

```bash
black --line-length 130 .  # Format code (line length: 130)
```

### Build/Release

```bash
flit build   # Build distribution
flit publish # Publish to PyPI
```

## Architecture

### Core Components

**pyrpm/spec.py** (562 lines) - Single-file implementation containing all
parsing logic

1. **Tag Parsing System** - Abstract base class `_Tag` with specialized
   subclasses:
   - `_NameValue`: Simple key-value tags (Name, Version, Summary, etc.)
   - `_List`: List-based tags (BuildRequires, Requires, etc.)
   - `_ListAndDict`: Tags that populate both list and dict (Source, Patch)
   - `_SetterMacroDef`: Global and local macro definitions (%global, %define)
   - Parse context tracks current subpackage and multiline states

2. **Main API Classes**:
   - `Spec`: Represents entire spec file, parses via `Spec.from_file()` or
     `Spec.from_string()`
   - `Package`: Represents main package or subpackage (from %package directives)
   - `Requirement`: Parses versioned dependencies with operators (>=, <=, =)

3. **Macro Expansion**: `replace_macros(string, spec)` - Expands RPM macros like
   `%{version}` into actual values

### Parsing Flow

1. `Spec.from_file(filename)` reads spec file line by line
2. Each line tested against registered `_tags` list (pattern matching)
3. Matching tag's `update()` method modifies Spec object and parse context
4. Parse context tracks current subpackage and multiline sections (description,
   changelog)
5. Macros stored in `spec.macros` dict for later expansion

### Data Access Patterns

- **Simple attributes**: `spec.name`, `spec.version`, `spec.summary`
- **Lists**: `spec.sources`, `spec.patches`, `spec.build_requires`,
  `spec.requires`
- **Dictionaries**: `spec.sources_dict["Source0"]`,
  `spec.patches_dict["Patch1"]`
- **Packages**: `spec.packages` (list) or `spec.packages_dict["package-name"]`
- **Subpackage attributes**: Each Package can override spec-level attributes

## Type Checking Configuration

mypy is configured with strict mode (mypy.ini):

- `python_version = 3.14` - Target version
- All strict flags enabled (disallow_untyped_calls, disallow_untyped_defs, etc.)
- Tests and examples directories have `ignore_errors = True`

## Linting Configuration

pylint (.pylintrc):

- Line length: 130
- Disabled checks: missing-docstring, invalid-name, too-few-public-methods,
  no-member, unused-argument, import-outside-toplevel

## Project Constraints

- **Python 3.10+** required (currently supports 3.10-3.14)
- **No external dependencies** - stdlib only for the library itself
- **Read-only parsing** - Does not modify or write spec files
- **Regex-based** - Not a complete formal parser
- **Incomplete coverage** - Parses common tags but not all spec file features
  (e.g., %include not supported)

## Testing

- Tests in `tests/` directory
- Test data (sample spec files) in `tests/data/`
- CI runs on Python 3.10-3.14 across Ubuntu, macOS, and Windows
- GitHub workflow also tests against Fedora's spec files (fedora-sources.yml)
