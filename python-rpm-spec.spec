%global srcname rpm-spec

# enable tests by default, disable with --without tests
%bcond_without tests

Name:           python3-%{srcname}
Version:        0.4
Release:        1%{?dist}
Summary:        Python module for parsing RPM spec files

License:        MIT
URL:            https://github.com/bkircher/python-rpm-spec
Source0:        https://github.com/bkircher/python-%{srcname}/archive/%{version}.tar.gz#/python-%{srcname}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
%if %{with tests}
BuildRequires:  python3-pytest
%endif

%{?python_provide:%python_provide python3-%{srcname}}

%description
python-rpm-spec is a Python module for parsing RPM spec files. RPMs are build
from a package's sources along with a spec file. The spec file controls how the
RPM is built. This module allows you to parse spec files and gives you simple
access to various bits of information that is contained in the spec file.

%prep
%autosetup -n python-%{srcname}-%{version}

%build
%py3_build

%install
%py3_install

%check
%if %{with tests}
py.test-%{python3_version} -vv tests || :
%endif

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/*

%changelog
* Thu Feb 09 2017 Benjamin Kircher <benjamin.kircher@gmail.com> - 0.4-1
- New version, allow disabling tests

* Fri Jan 27 2017 Benjamin Kircher <benjamin.kircher@gmail.com> - 0.3-1
- New version

* Thu Jan 26 2017 Benjamin Kircher <benjamin.kircher@gmail.com> - 0.2-1
- Initial spec
