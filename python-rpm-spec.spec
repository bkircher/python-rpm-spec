%global srcname rpm-spec

Name:           python3-%{srcname}
Version:        0.2
Release:        1%{?dist}
Summary:        Python module for parsing RPM spec files

License:        MIT
URL:            https://github.com/bkircher/python-rpm-spec
Source0:        https://github.com/bkircher/python-%{srcname}/archive/%{version}.tar.gz#/python-%{srcname}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-pytest

%description
%{name} is a Python module for parsing RPM spec files. RPMs are build from a
package's sources along with a spec file. The spec file controls how the RPM is
built. This module allows you to parse spec files and gives you simple access
to various bits of information that is contained in the spec file.

%prep
%setup -q -n python-%{srcname}-%{version}

%build
%py3_build

%install
%py3_install

%check
py.test-3

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/*

%changelog
* Thu Jan 26 2017 Benjamin Kircher <benjamin.kircher@gmail.com>
- Initial spec
