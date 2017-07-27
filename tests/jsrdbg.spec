%global commit       26f9f2b27c04b4aec9cd67baaf9a0a206bbbd5c7
%global commitdate   20170727

Name:		jsrdbg
Version:	0.0.7
Release:	4.%{commitdate}git%(c=%{commit}; echo ${c:0:7} )%{?dist}
Summary:	JavaScript Remote Debugger for SpiderMonkey
Group:		Development/Debuggers
License:	LGPLv2+
URL:		https://github.com/swojtasiak/jsrdbg
Source0:	https://github.com/swojtasiak/%{name}/archive/%{commit}.tar.gz#/%{name}-%{commit}.tar.gz

BuildRequires:	autoconf-archive
BuildRequires:	libtool
BuildRequires:	gettext
BuildRequires:	mozjs24-devel
BuildRequires:	readline-devel
BuildRequires:	gettext-devel
BuildRequires:	gcc-c++
Requires:	mozjs24

%description
%{name} is an implementation of a high level debugging protocol for the
SpiderMonkey JavaScript engine which is available as a shared library. The
library can be used to integrate debugging facilities into an existing
application leveraging SpiderMonkey. There are several integration
possibilities including exposition of the high level debugger API locally
directly to the application and even exposing it to remote clients using TCP.

%package devel
Summary: Header files, libraries and development documentation for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains the header files, static libraries, and development
documentation for %{name}. If you like to develop programs using %{name}, you
will need to install %{name}-devel.

%package -n jrdb
Summary: A command line debugger client for %{name}
Group: Development/Debuggers
License: GPLv2+

%description -n jrdb
This package contains a command line client that allows to connect to a remote
JavaScript debugger.

%prep
%autosetup

%build
autoreconf -i
%configure
make %{?_smp_mflags}

%check
make check

%install
%make_install DESTDIR=%{buildroot}

%files
%license COPYING
%doc README.md
%{_libdir}/libjsrdbg.so.*

%files devel
%{_includedir}/jsrdbg
%{_libdir}/libjsrdbg.a
%{_libdir}/libjsrdbg.la
%{_libdir}/libjsrdbg.so
%{_libdir}/pkgconfig/libjsrdbg.pc
%{_datadir}/cmake/Modules/FindJSRDBG.cmake

%files -n jrdb
%{_bindir}/jrdb

%changelog
* Thu Jul 27 2017 Benjamin Kircher <benjamin.kircher@gmail.com> - 0.0.7-4.20170727git26f9f2b
- New snapshot of upstream master

* Thu Jul 20 2017 Benjamin Kircher <benjamin.kircher@gmail.com> - 0.0.7-3.20170720git89613fc
- New snapshot of upstream master

* Tue Apr 25 2017 Benjamin Kircher <benjamin.kircher@gmail.com> - 0.0.7-2
- Fix missing BR

* Sat Apr 22 2017 Benjamin Kircher <benjamin.kircher@gmail.com> - 0.0.7-1
- New upstream version
- Install CMake find script
- Add check section

* Fri Dec 23 2016 Benjamin Kircher <kircher@otris.de> - 0.0.6-3
- Separate package for jrdb binary and other improvements

* Thu Mar 03 2016 Benjamin Kircher <kircher@otris.de> - 0.0.6-2
- Devel package

* Wed Mar 02 2016 Benjamin Kircher <kircher@otris.de> - 0.0.6-1
- Initial spec
