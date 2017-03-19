#
# spec file for package attica-qt5
#
# Copyright (c) 2017 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


%define sonum   5
%define rname attica
%define _libname KF5Attica
%define _tar_path 5.31
Name:           attica-qt5
Version:        5.32.0
Release:        0
Summary:        Open Collaboration Service client library
License:        LGPL-2.1+
Group:          System/GUI/KDE
Url:            https://projects.kde.org/attica
Source:         http://download.kde.org/stable/frameworks/%{_tar_path}/%{rname}-%{version}.tar.xz
Source99:       baselibs.conf
BuildRequires:  cmake >= 3.0
BuildRequires:  extra-cmake-modules >= %{_tar_path}
BuildRequires:  fdupes
BuildRequires:  kf5-filesystem
BuildRequires:  pkg-config
BuildRequires:  cmake(Qt5Core) >= 5.6.0
BuildRequires:  cmake(Qt5Network) >= 5.6.0
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
Attica is a library to access Open Collaboration Service servers.

%package -n lib%{_libname}%{sonum}
Summary:        Open Collaboration Service client library - development files
Group:          System/GUI/KDE
%requires_ge libQt5Core5
%requires_ge libQt5Network5

%description -n lib%{_libname}%{sonum}
Attica is a library to access Open Collaboration Service servers.

%package -n attica-qt5-devel
Summary:        Open Collaboration Service client library - development files
Group:          Development/Libraries/C and C++
Requires:       lib%{_libname}%{sonum} = %{version}
Requires:       cmake(Qt5Core) >= 5.6.0
Requires:       cmake(Qt5Network) >= 5.6.0

%description -n attica-qt5-devel
Development files for attica, Attica a library to access Open Collaboration Service servers.

%prep
%setup -q -n %{rname}-%{version}

%build
  %cmake_kf5 -d build
  %make_jobs

%install
  %kf5_makeinstall -C build
  %fdupes %{buildroot}

%post -n lib%{_libname}%{sonum} -p /sbin/ldconfig

%postun -n lib%{_libname}%{sonum} -p /sbin/ldconfig

%files -n lib%{_libname}%{sonum}
%defattr(-,root,root)
%doc COPYING* README*
%{_libqt5_libdir}/lib%{_libname}*.so.*

%files -n attica-qt5-devel
%defattr(-,root,root)
%{_kf5_libdir}/cmake/KF5Attica/
%{_libqt5_libdir}/lib%{_libname}*.so
%{_libqt5_libdir}/pkgconfig/libKF5Attica.pc
%{_kf5_includedir}/
%{_kf5_mkspecsdir}/qt_Attica.pri

%changelog
