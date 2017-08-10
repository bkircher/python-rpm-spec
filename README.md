# python-rpm-spec

[![Build Status](https://travis-ci.org/bkircher/python-rpm-spec.svg?branch=master)](https://travis-ci.org/bkircher/python-rpm-spec)

python-rpm-spec is a Python module for parsing RPM spec files.

RPMs are build from a package's sources along with a spec file. The spec file
controls how the RPM is built. This module allows you to parse spec files and
gives you simple access to various bits of information that is contained in the
spec file.

## Features
* No extra dependencies other than Python 3
* Available on all platforms, parse spec files on Windows

## Examples
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

## Install

python-rpm-spec is hosted on PyPI - the Python Package Index. So all you need to do is

```bash
$ pip install python-rpm-spec
```

in your virtual environment.

Alternatively, if you run Fedora, you can enable a copr repository and use the
package manager to install a python-rpm-spec as a normal package in your
system.

```bash
$ sudo dnf copr enable bkircher/python-rpm-spec  # Enable copr repo
$ sudo dnf install -y python3-rpm-spec  # Install the package
```

## Dependencies
Except Python 3 no extra dependencies are required. No Python 2, sorry.

## Current status
This module does not parse everything of a spec file. Only the pieces I needed.
So there is probably still plenty of stuff missing. However, it should not be
terribly complicated to add support for the missing pieces.

## Development
If you want to hack on this module you could start with following recipe:

```bash
$ git clone https://github.com/bkircher/python-rpm-spec.git  # Clone the repo
$ cd python-rpm-spec  # Change into the source directory
$ mkdir .venv && python3 -m venv .venv  # Create a virtual environment
$ source .venv/bin/activate  # Activate it
$ pip install pytest  # Install py.test
$ pytest  # Execute all tests
```
Happy hacking!

<!-- vim: et sw=4 ts=4:
-->
