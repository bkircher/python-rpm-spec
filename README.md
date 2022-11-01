# python-rpm-spec

[![pytest status](https://github.com/bkircher/python-rpm-spec/workflows/tests/badge.svg)](https://github.com/bkircher/python-rpm-spec/actions)
[![PyPI version](https://badge.fury.io/py/python-rpm-spec.svg)](https://badge.fury.io/py/python-rpm-spec)

python-rpm-spec is a Python library for parsing RPM spec files.

*tl;dr*
If you want to quickly parse a spec file on the command line you might want to
give `rpmspec --parse` a try.

```sh
rpmspec --parse file.spec | awk '/Source/ {print $2}'
```

If you write Python, have no `/usr/bin/rpm` around, or want to do something
slightly more complicated, try using this Python module.

RPMs are build from a package's sources along with a spec file. The spec file
controls how the RPM is built. This module allows you to parse spec files and
gives you simple access to various bits of information that is contained in the
spec file.

## Features

* No extra dependencies other than Python 3
* Available on all platforms, parse spec files on Windows

## Supported Python versions

All [current Python branches](https://devguide.python.org/versions/#versions) are supported.

| Python Version | Supported Until |
| :------------- | --------------: |
| 3.11           | 2027-10         |
| 3.10           | 2026-10         |
| 3.9            | 2025-10         |
| 3.8            | 2024-10         |
| 3.7            | 2023-06-27      |

Also works on 3.6 and possibly older versions but they might break anytime.

## Install

python-rpm-spec is [hosted](https://pypi.org/project/python-rpm-spec/) on PyPI -
the Python Package Index. So all you need to do is

```sh
python -m pip install python-rpm-spec==0.13
```

in your virtual environment.

## Examples

This is how you access a spec file's various definitions:

```python
from pyrpm.spec import Spec, replace_macros

spec = Spec.from_file('llvm.spec')
print(spec.version)  # 3.8.0
print(spec.sources[0])  # http://llvm.org/releases/%{version}/%{name}-%{version}.src.tar.xz
print(replace_macros(spec.sources[0], spec))  # http://llvm.org/releases/3.8.0/llvm-3.8.0.src.tar.xz

for package in spec.packages:
    print(f'{package.name}: {package.summary if hasattr(package, "summary") else spec.summary}')

    # llvm: The Low Level Virtual Machine
    # llvm-devel: Libraries and header files for LLVM
    # llvm-doc: Documentation for LLVM
    # llvm-libs: LLVM shared libraries
    # llvm-static: LLVM static libraries

```

Example showing how to retrieve named source or patch files from a spec:

```python
from pyrpm.spec import Spec

spec = Spec.from_file('llvm.spec')

# Access sources and patches via name
for k, v in spec.sources_dict.items():
    print(f'{k} → {v}')

# Source0 → http://llvm.org/releases/%{version}/%{name}-%{version}.src.tar.xz
# Source100 → llvm-config.h

# Or as a list with indices and so on
for source in spec.sources:
    print(source)

# http://llvm.org/releases/%{version}/%{name}-%{version}.src.tar.xz
# llvm-config.h
```

Example showing how to get versioned `BuildRequires:` and `Requires:` out of a
spec file:

```python
from pyrpm.spec import Spec

spec = Spec.from_file('attica-qt5.spec')

# Access sources and patches via name
for br in spec.build_requires:
    print(f'{br.name} {br.operator} {br.version}' if br.version else f'{br.name}')

# cmake >= 3.0
# extra-cmake-modules >= %{_tar_path}
# fdupes
# kf5-filesystem
# pkg-config
# cmake(Qt5Core) >= 5.6.0
# cmake(Qt5Network) >= 5.6.0
```

If you want that the library [create warnings](https://docs.python.org/3/library/warnings.html) during parsing, for example on
unknown macros, set `warnings_enabled` to `True`:

```python
import pyrpm.spec

pyrpm.spec.warnings_enabled = True
# …
```

## Dependencies

Except Python 3 no extra dependencies are required.

## Current status

This module does not parse everything of a spec file. Only the pieces I needed.
So there is probably still plenty of stuff missing. However, it should not be
terribly complicated to add support for the missing pieces.

## Development

If you want to hack on this module you could start with following recipe:

```sh
git clone https://github.com/bkircher/python-rpm-spec.git  # Clone the repo
cd python-rpm-spec  # Change into the source directory
python3 -m venv .venv  # Create a virtual environment
source .venv/bin/activate  # Activate it
pip install -r dev-requirements.txt  # Install dependencies for development
pytest  # Execute all tests
pytest --mypy  # Run the type checker
```

## Further references

Take a look at the excellent [RPM Packaging Guide](https://rpm-guide.readthedocs.io/en/latest/index.html), especially the section
[What is a SPEC File?](https://rpm-guide.readthedocs.io/en/latest/rpm-guide.html#what-is-a-spec-file)

Happy hacking!
