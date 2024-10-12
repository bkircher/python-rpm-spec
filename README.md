# python-rpm-spec

[![pytest status](https://github.com/bkircher/python-rpm-spec/actions/workflows/test.yml/badge.svg)](https://github.com/bkircher/python-rpm-spec/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/python-rpm-spec.svg)](https://badge.fury.io/py/python-rpm-spec)

python-rpm-spec is a Python-only library for parsing RPM spec files.

_tl;dr_ If you want to quickly parse a spec file on the command line you might
want to give `rpmspec --parse` a try.

```sh
rpmspec --parse file.spec | awk '/Source/ {print $2}'
```

If you write Python, have no `/usr/bin/rpm` around, or want to do something
slightly more complicated, try using this Python library.

RPMs are build from a package's sources along with a spec file. The spec file
controls how the RPM is built. This library allows you to parse spec files and
gives you simple access to various bits of information that is contained in the
spec file.

## Features

- No extra dependencies other than Python 3.
- Available on all platforms, parse spec files on Windows.
- Read-only (for manipulating spec files see [Alternatives](#alternatives)
  below).

## Supported Python versions

All [current Python branches](https://devguide.python.org/versions/#versions)
are supported.

| Python Version | Supported Until |
| :------------- | --------------: |
| 3.13           |         2029-10 |
| 3.12           |         2028-10 |
| 3.11           |         2027-10 |
| 3.10           |         2026-10 |
| 3.9            |         2025-10 |

## Install

python-rpm-spec is [hosted](https://pypi.org/project/python-rpm-spec/) on PyPI -
the Python Package Index. All you need to do is

```sh
pip install python-rpm-spec
```

in your virtual environment.

## Examples

The libraries main API objects are the `Spec` object, representing an entire
spec file and the `replace_macros` function which is used to expand macro's into
absolute string values.

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

If you want that the library
[create warnings](https://docs.python.org/3/library/warnings.html) during
parsing, for example on unknown macros, set `warnings_enabled` to `True`:

```python
import pyrpm.spec

pyrpm.spec.warnings_enabled = True
# …
```

## Dependencies

No extra dependencies are required except for Python 3.8 or newer.

## Current status

This library is an ambitious Python script that became a library. It is not
complete and it does not fit every use case.

- It is probably very slow and it relies on regular expressions for parsing.
- It does not parse everything in a spec file, only the pieces myself and others
  needed so far.

So there is probably still plenty of stuff missing (i.e. support for
[`%include`](https://github.com/bkircher/python-rpm-spec/issues/51)). However,
it should not be too complicated to add support for the missing pieces.

Also note that there is a
[GitHub workflow](https://github.com/bkircher/python-rpm-spec/actions/workflows/fedora-sources.yml)
that runs the parser on Fedora's spec files.

## Alternatives

Here is a list of alternatives to this library:

- [packit/specfile](https://github.com/packit/specfile) - Allows parsing and,
  different to python-rpm-spec, the manipulation of spec files. Part of packit.
  Actively developed as of March 2023.
- If you are on a Linux system that has the RPM package manager installed,
  consider using system tools like
  - `rpmspec(8)` from rpm-build package. Example: `rpmspec --parse foo.spec`
    will parse a spec file to stdout, expanding all the macros installed on the
    system. Still relies on `$HOME/rpmbuild` to work.
  - `rpmdev-spectool(1)` from rpmdevtools package. Example:
    `spectool --get-files foo.spec` will download all sources and patches from a
    spec file.

  The parsers of those system tools are probably more up to date and less buggy
  than this library.

## Development

If you want to hack on this library you could start with following recipe:

```sh
git clone https://github.com/bkircher/python-rpm-spec.git  # Clone the repo
cd python-rpm-spec  # Change into the source directory
python3 -m venv .venv  # Create a virtual environment
source .venv/bin/activate  # Activate it
pip install -r requirements.txt  # Install dependencies for development
pytest  # Execute all tests
mypy . # Run the type checker
```

That's it. Make sure to check out the
[issue tracker](https://github.com/bkircher/python-rpm-spec/issues) for things
to work on or open a
[new issue](https://github.com/bkircher/python-rpm-spec/issues/new/choose) to
let others know what you are working on.

## Further references

- [RPM project documentation](https://rpm.org/documentation.html) with a couple
  of links to books or Fedora project documentation.
- Take a look at the excellent
  [RPM Packaging Guide](https://rpm-guide.readthedocs.io/en/latest/index.html),
  especially the section
  [What is a SPEC File?](https://rpm-guide.readthedocs.io/en/latest/rpm-guide.html#what-is-a-spec-file)

Happy hacking!
