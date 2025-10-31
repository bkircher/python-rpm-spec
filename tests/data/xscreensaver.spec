%define name          xscreensaver

%define mainversion   6.06
#%%undefine extratarver   1
#%%define beta_ver      b2
%undefine beta_ver


%define modular_conf  1
%define split_getimage   0
%if 0%{?fedora} >= 14
%define split_getimage   1
%endif

%define fedora_rel    2

%global use_clang_as_cc 0
%global use_clang_analyze 0
%global use_cppcheck   0
%global use_gcc_strict_sanitize 0
%global use_gcc_trap_on_sanitize 0
%global use_gcc_analyzer 0

%global enable_animation 1
%undefine extrarel

%global flagrel %{nil}
%if 0%{?use_cppcheck} >= 1
%global flagrel %{flagrel}.CPPCHECK
%endif
%if 0%{?use_gcc_strict_sanitize} >= 1
%global flagrel %{flagrel}.SAN
%endif
%if 0%{?use_clang_analyze} >= 1
%global flagrel %{flagrel}.clang_alz
%endif

%global toolchain     gcc
%if 0%{?use_clang_as_cc} >= 1
%global toolchain     clang
%endif

# EPEL6
%{!?__git:%define __git git}

%if 0%{?fedora}
%define default_text  %{_sysconfdir}/fedora-release
%else
%define default_text  %{_sysconfdir}/system-release
%endif
%define default_URL   http://planet.fedoraproject.org/rss20.xml

%define pam_ver       0.80-7
%define autoconf_ver  2.53

%define update_po     1
%define build_tests   0

%global support_setcap 0
%if 0%{?fedora} >= 31
# TODO write selinux policy for selinux-policy-mls 
# (currently works with selinux-policy-targeted)
#%%global support_setcap 1
%endif
# enable xscreensaver-systemd for F-33
%global  support_systemd 0
%if 0%{?fedora} >= 33
%global  support_systemd 1
%endif

%undefine        _changelog_trimtime


Summary:         X screen saver and locker
Name:            %{name}
Version:         %{mainversion}
Release:         %{?beta_ver:0.}%{fedora_rel}%{?beta_ver:.%beta_ver}%{?dist}%{flagrel}%{?extrarel}
Epoch:           1
License:         MIT
URL:             http://www.jwz.org/xscreensaver/
Source0:         http://www.jwz.org/xscreensaver/xscreensaver-%{mainversion}%{?beta_ver}%{?extratarver:.%extratarver}.tar.gz
%if %{modular_conf}
Source10:        update-xscreensaver-hacks
%endif
%if 0%{?fedora} >= 12
Source11:        xscreensaver-autostart
Source12:        xscreensaver-autostart.desktop
%endif
# wrapper script for switching user (bug 1878730)
Source13:        xscreensaver-newlogin-wrapper
Source100:       ja.po
##
## Patches
##
# bug 129335
Patch1:          xscreensaver-5.45-0001-barcode-glsnake-sanitize-the-names-of-modes.patch
## Patches already sent to the upsteam
## Patches which must be discussed with upstream
# See bug 472061
Patch21:         xscreensaver-6.06-webcollage-default-nonet.patch
# misc: kill gcc warn_unused_result warnings
Patch3607:       xscreensaver-5.36-0007-misc-kill-gcc-warn_unused_result-warnings.patch
# switch_page_cb: backport debian fix for DPMS settings issue (debian bug 1031076)
Patch4601:       xscrensaver-6.06-0001-switch_page_cb-backport-debian-1031076-for-DPMS-settings.patch
# Fedora specific
# window_init: search parenthesis first for searching year
Patch10001:     xscreensaver-6.00-0001-screensaver_id-search-parenthesis-first-for-searchin.patch
# dialog.c: window_init: show more version string
Patch10003:     xscreensaver-6.00-0003-dialog.c-window_init-show-more-version-string.patch
#
# gcc warning cleanup
# Some cppcheck cleanup
#
# Debugging patch
# Not apply by default
# XIO: print C backtrace on error
Patch13501:      xscreensaver-5.35-0101-XIO-print-C-backtrace-on-error.patch
#
# Patches end
Requires:        xscreensaver-base = %{epoch}:%{version}-%{release}
Requires:        xscreensaver-extras = %{epoch}:%{version}-%{release}
Requires:        xscreensaver-gl-extras = %{epoch}:%{version}-%{release}

%package base
Summary:         A minimal installation of xscreensaver

%if 0%{?use_clang_analyze} >= 1
BuildRequires:   clang-analyzer
BuildRequires:   clang
%endif
%if 0%{?use_clang_as_cc}
BuildRequires:   clang
%endif
%if 0%{?use_cppcheck}
BuildRequires:   cppcheck
%endif
%if 0%{?use_gcc_strict_sanitize}
BuildRequires:   libasan
BuildRequires:   libubsan
%endif
BuildRequires:   make
BuildRequires:   git
BuildRequires:   autoconf
BuildRequires:   automake
BuildRequires:   intltool
BuildRequires:   bc
BuildRequires:   desktop-file-utils
BuildRequires:   gawk
BuildRequires:   gettext
BuildRequires:   libtool
BuildRequires:   pam-devel > %{pam_ver}
BuildRequires:   sed
# Use pseudo symlink
# BuildRequires:   xdg-utils
BuildRequires:   xorg-x11-proto-devel
# extrusioni
%if 0%{?fedora} >= 13
BuildRequires:   libgle-devel
%endif
BuildRequires:   libX11-devel
BuildRequires:   libXScrnSaver-devel
# xscreensaver 6.00
#BuildRequires:   libXcomposite-devel
BuildRequires:   libXext-devel
# From xscreensaver 5.12, write explicitly
BuildRequires:   libXi-devel
BuildRequires:   libXinerama-devel
# Dropped from 6.00
# BuildRequires:   libXmu-devel
# xscreensaver 5.39: check if the following can be removed
BuildRequires:   libXpm-devel
# xscreensaver 5.39
BuildRequires:   libpng-devel
# Write explicitly
BuildRequires:   libXrandr-devel
BuildRequires:   libXt-devel
# libXxf86misc removed from F-31
#BuildRequires:   libXxf86misc-devel
BuildRequires:   libXxf86vm-devel
# XScreenSaver 5.31
BuildRequires:   libXft-devel
BuildRequires:   pkgconfig(gtk+-3.0) >= 2.22.0
BuildRequires:   pkgconfig(gmodule-2.0)
BuildRequires:   pkgconfig(libxml-2.0)
BuildRequires:   pkgconfig(gio-2.0)
# Write explicitly below, especially
# for F-23 gdk_pixbuf package splitting
BuildRequires:   pkgconfig(gdk-pixbuf-2.0)
BuildRequires:   libjpeg-devel
BuildRequires:   libglade2-devel
%if 0%{?support_setcap} >= 1
BuildRequires:   pkgconfig(libcap)
%endif
# From F-33, enable systemd support
%if 0%{?support_systemd} >= 1
BuildRequires:   pkgconfig(libsystemd)
%endif
%if 0%{?fedora}
BuildRequires:   %{default_text}
%endif
# For https://fedoraproject.org/wiki/Packaging:Perl#Build_Dependencies
# https://fedoraproject.org/wiki/Changes/Build_Root_Without_Perl
BuildRequires:    perl-interpreter
BuildRequires:    perl-generators
# For --with-login-manager option
%if 0%{?fedora} >= 14
# Use pseudo symlink, not writing BR: gdm
#BuildRequires:   gdm
%endif
Requires:        %{_sysconfdir}/pam.d/system-auth
Requires:        pam > %{pam_ver}
# For xdg-open
Requires:        xdg-utils
%if ! %{split_getimage}
Requires:        appres
%endif
# For switch user wrapper
Requires:        %{_bindir}/pidof
%if 0%{?build_tests} < 1
# Obsoletes but not Provides
Obsoletes:       xscreeensaver-tests < %{epoch}:%{version}-%{release}
%endif
# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1030659
# XScreenSaver 6.06 xscreensaver-settings now needs xscreensaver-gl-visual
Requires:        %{name}-gl-base = %{epoch}:%{version}-%{release}

%package extras-base
Summary:         A base package for screensavers
%if 0%{?fedora} < 19
Requires:        %{name}-base = %{epoch}:%{version}-%{release}
%endif
Requires:        appres

%package extras
Summary:         An enhanced set of screensavers
%if 0%{?fedora} >= 19
# Does not available on EPEL7
BuildRequires:   desktop-backgrounds-basic
%else
BuildRequires:   gnome-backgrounds
%endif
Requires:        %{name}-base = %{epoch}:%{version}-%{release}
%if %{split_getimage}
Requires:        %{name}-extras-base = %{epoch}:%{version}-%{release}
%endif

%package gl-base
Summary:         A base package for screensavers that require OpenGL

%package gl-extras
Summary:         An enhanced set of screensavers that require OpenGL
Provides:        xscreensaver-gl = %{epoch}:%{version}-%{release}
Obsoletes:       xscreensaver-gl <= 1:5.00
BuildRequires:   libGL-devel
BuildRequires:   libGLU-devel
%if %{modular_conf}
Requires:        %{name}-gl-base = %{epoch}:%{version}-%{release}
%else
Requires:        %{name}-base = %{epoch}:%{version}-%{release}
%endif
%if %{split_getimage}
Requires:        %{name}-extras-base = %{epoch}:%{version}-%{release}
%endif

%package extras-gss
Summary:         Desktop files of extras for other screensaver
Requires:        %{name}-extras = %{epoch}:%{version}-%{release}

%package gl-extras-gss
Summary:         Desktop files of gl-extras for other screensaver
Requires:        %{name}-gl-extras = %{epoch}:%{version}-%{release}

%package tests
Summary:         Test programs related to XScreenSaver
Requires:        %{name}-base = %{epoch}:%{version}-%{release}

%package clang-analyze
Summary:         Clang analyze result log

%package cppcheck
Summary:         cppcheck result log


%description
A modular screen saver and locker for the X Window System.
More than 200 display modes are included in this package.

This is a metapackage for installing all default packages
related to XScreenSaver.

%description -l fr
Un économiseur d'écran modulaire pour le système X Window.
Plus de 200 modes d'affichages sont inclus dans ce paquet.

This is a metapackage for installing all default packages
related to XScreenSaver.

%description base
A modular screen saver and locker for the X Window System.
This package contains the bare minimum needed to blank and
lock your screen.  The graphical display modes are the
"xscreensaver-extras" and "xscreensaver-gl-extras" packages.

%description -l fr base 
Un économiseur d'écran modulaire pour le système X Window.
Ce paquet contient le minimum vital pour éteindre et verouiller
votre écran. Les modes d'affichages graphiques sont inclus
dans les paquets "xscreensaver-extras" et "xscreensaver-gl-extras".

%description extras-base
This package contains common files to make screensaver hacks
work for XScreenSaver.

%description extras
A modular screen saver and locker for the X Window System.
This package contains a variety of graphical screen savers for
your mind-numbing, ambition-eroding, time-wasting, hypnotized
viewing pleasure.

%description -l fr extras
Un économiseur d'écran modulaire pour le système X Window.
Ce paquet contient une pléthore d'économiseurs d'écran graphiques
pour votre plaisir des yeux.

%description gl-base
A modular screen saver and locker for the X Window System.
This package contains minimal files to make screensaver hacks
that require OpenGL work for XScreenSaver.

%description gl-extras
A modular screen saver and locker for the X Window System.
This package contains a variety of OpenGL-based (3D) screen
savers for your mind-numbing, ambition-eroding, time-wasting,
hypnotized viewing pleasure.

%description -l fr gl-extras
Un économiseur d'écran modulaire pour le système X Window.
Ce paquet contient une pléthore d'économiseurs d'écran basés sur OpenGL (3D)
pour votre plaisir des yeux.

%description extras-gss
This package contains desktop files of extras screensavers
for other screensaver compatibility.

%description gl-extras-gss
This package contains desktop files of gl-extras screensavers
for other screensaver compatibility.

%description tests
This package contains some test programs to debug XScreenSaver.

%description clang-analyze
This package contains Clang analyze result of XScreenSaver.

%description cppcheck
This package contains cppcheck result of XScreenSaver.


%prep
%setup -q -n %{name}-%{mainversion}%{?beta_ver}

cat > .gitignore <<EOF
configure
config.guess
config.sub
aclocal.m4
config.h.in
config.rpath
OSX
EOF

# Firstly clean this
rm -f driver/XScreenSaver_ad.h

# chmod
find . -name \*.c -exec chmod ugo-x {} \;

%__git init
%__git config user.email "xscreensaver-owner@fedoraproject.org"
%__git config user.name "XScreenSaver owners"
%__git add .
%__git commit -m "base" -q

%__cat %PATCH1 | %__git am
%__cat %PATCH21 | %__git am

#%%__cat %PATCH3607 | %__git am
%__cat %PATCH4601 | %__git am
%__cat %PATCH10001 | %__git am
%__cat %PATCH10003 | %__git am

#%%__cat %PATCH13501 | %%__git am

change_option(){
   set +x
   ADFILE=$1
   if [ ! -f ${ADFILE}.opts ] ; then
      cp -p $ADFILE ${ADFILE}.opts
   fi
   shift

   for ARG in "$@" ; do
      TYPE=`echo $ARG | sed -e 's|=.*$||'`
      VALUE=`echo $ARG | sed -e 's|^.*=||'`

      eval sed -i \
         -e \'s\|\^\\\(\\\*$TYPE\:\[ \\t\]\[ \\t\]\*\\\)\[\^ \\t\]\.\*\$\|\\1$VALUE\|\' \
         $ADFILE
   done
   set -x
}

silence_hack(){
   set +x
   ADFILE=$1
   if [ ! -f ${ADFILE}.hack ] ; then
      cp -p $ADFILE ${ADFILE}.hack
   fi
   shift

   for hack in "$@" ; do
      eval sed -i \
         -e \'\/\^\[ \\t\]\[ \\t\]\*$hack\/s\|\^\|-\|g\' \
         -e \'s\|\^@GL_\.\*@.*\\\(GL\:\[ \\t\]\[ \\t\]\*$hack\\\)\|-\\t\\1\|g\' \
         $ADFILE
   done
   set -x
}

%global PATCH_desc \
# change some files to UTF-8
for f in \
%if 0
   driver/XScreenSaver.ad.in \
%endif
   hacks/glx/sproingies.man \
   ; do
   iconv -f ISO-8859-1 -t UTF-8 $f > $f.tmp || cp -p $f $f.tmp
   touch -r $f $f.tmp
   mv $f.tmp $f
done
%__git commit -m "%PATCH_desc" -a

%global PATCH_desc \
# Change some options \
# For grabDesktopImages, lock, see bug 126809
change_option driver/XScreenSaver.ad.in \
   captureStderr=False \
   passwdTimeout=0:00:15 \
   grabDesktopImages=False \
   lock=True \
   splash=False \
   ignoreUninstalledPrograms=True \
   textProgram=fortune\ -s \
%if 0%{?fedora} >= 12
   textURL=%{default_URL}
%endif
%__git commit -m "%PATCH_desc" -a

# peepers: 5.39: too scary (mtasaka)
# headroom: 5.45: too scary (mtasaka)
%global PATCH_desc \
# Disable the following hacks by default \
# (disable, not remove)
silence_hack driver/XScreenSaver.ad.in \
   bsod flag \
   peepers \
   headroom \
   %{nil}
%__git commit -m "%PATCH_desc" -a

%global PATCH_desc \
# Record time, EVR
eval sed -i.ver \
   -e \'s\|version \[45\]\.\[0-9a-z\]\[0-9a-z\]\*\|version %{version}-`echo \
      %{release} | sed -e '/IGNORE THIS/s|\.[a-z][a-z0-9].*$||'`\|\' \
      driver/XScreenSaver.ad.in

eval sed -i.date \
   -e \'s\|\[0-9\].\*-.\*-20\[0-9\]\[0-9\]\|`LANG=C LC_ALL=C date -u +'%%d-%%b-%%Y'`\|g\' \
   driver/XScreenSaver.ad.in

eval sed -i.ver \
   -e \'s\|\(\[0-9\].\*-.\*-20\[0-9\]\[0-9\]\)\|\(`LANG=C LC_ALL=C \
      date -u +'%%d-%%b-%%Y'`\)\|g\' \
   -e \'s\|\\\([56]\\\.\[0-9\]\[0-9\]\\\)[a-z]\[0-9\]\[0-9\]\*\|\\\1\|\' \
   -e \'s\|[56]\\\.\[0-9\]\[0-9\]\|%{version}-`echo %{release} | \
      sed -e '/IGNORE THIS/s|\.[a-zA-Z][a-zA-Z0-9].*$||'`\|\' \
   -e \'s\|\\\(XSCREENSAVER_RELEASED\\\)\.\*\|\\\1 ${SOURCE_DATE_EPOCH}\|\' \
   utils/version.h
%__git commit -m "%PATCH_desc" -a

%global PATCH_desc \
# Move man entry to 6x (bug 197741)
for f in `find hacks -name Makefile.in` ; do
   sed -i.mansuf \
      -e '/^mansuffix/s|6|6x|'\
      $f
done
%__git commit -m "%PATCH_desc" -a

%global PATCH_desc \
# Search first 6x entry, next 1 entry for man pages
sed -i.manentry -e 's@man %%s@man 6x %%s 2>/dev/null || man 1 %%s @' \
   driver/XScreenSaver.ad.in
%__git commit -m "%PATCH_desc" -a

# Suppress rpmlint warnings.
# suppress about pam config (although this is 
# not the fault of xscreensaver.pam ......).
#
# From xscreensaver-5.15-10, no longer do this
%if 0
sed -i.rpmlint -n -e '1,5p' driver/xscreensaver.pam
%endif

if [ -x %{_datadir}/libtool/config.guess ]; then
  # use system-wide copy
   cp -p %{_datadir}/libtool/config.{sub,guess} .
fi

%global PATCH_desc \
# test-fade: give more time between fading
sed -i.delay -e 's| delay = 2| delay = 3|' driver/test-fade.c
%__git commit -m "%PATCH_desc" -a

%global PATCH_desc \
# test-grab: testing time too long, setting time 15 min -> 20 sec
sed -i.delay -e 's|60 \* 15|20|' driver/test-grab.c
%__git commit -m "%PATCH_desc" -a

# Well, clang misinterpretates how gcc / autoconf uses -Wunknown-warning-option ....
sed -i 's|-Wunknown-warning-option|-Wfoo-bar-baz|' ax_pthread.m4
%__git commit -m "Really use unknowing warning option" -a

# xscreensaver 6.03: manually fix po/Makefile.in.in
# ca.po seems broken
pushd po
sed -i Makefile.in.in \
	-e "\@^POFILES[ \t]*=@s@^.*@POTFILES\t=$(ls -1 *po | grep -v ca.po | while read f ; do echo -n -e " $f" ; done)@" \
	-e "\@^GMOFILES[ \t]*=@s@^.*@GMOTFILES\t=$(ls -1 *po | grep -v ca.po | while read f ; do echo -n -e " ${f%.po}.gmo" ; done)@" \
	-e "\@^CATALOGS[ \t]*=@s@^.*@CATALOGS\t=$(ls -1 *po | grep -v ca.po | while read f ; do echo -n -e " ${f%.po}.gmo" ; done)@" \
	-e "\@^CATOBJEXT[ \t]*=@s@^.*@CATOBJEXT\t= .gmo@" \
	-e "\@^INSTOBJEXT[ \t]*=@s@^.*@INSTOBJEXT\t= .mo@" \
	-e "\@^MKINSTALLDIRS[ \t]*=@s@^.*@MKINSTALLDIRS\t= install -d@" \
	%{nil}
popd
%__git commit -m "Manually fix po files entry" -a

# %%configure adds --disable-dependency-tracking, don't fail with that for now
sed -i configure.ac \
	-e "$(($(sed -n '\@ac_unrecognized_opts@=' configure.ac | head -n 1) + 2))s|exit 2|true exit 2|"
%__git commit -m "Don't make configure fail with unrecognized option" -a

touch config.rpath
aclocal
autoconf
autoheader

%build

archdir=`sh ./config.guess`
[ -d $archdir ] || mkdir $archdir
cd $archdir

# Create temporary path and symlink
rm -rf ./TMPBINDIR

# Make it sure that perl interpreter is recognized
# as /usr/bin/perl, not /bin/perl so as not to make
# /bin/perl added as rpm dependency
export PATH=/usr/bin:$PATH

mkdir TMPBINDIR
pushd TMPBINDIR/
export PATH=$(pwd):$PATH

# xdg-open
ln -sf /bin/true xdg-open
popd
# gtk-update-icon-cache
ln -sf /bin/true gtk-update-icon-cache

# Set optflags first
%set_build_flags

# Doesn't work well when generating debuginfo...
# export CFLAGS="$(echo $CFLAGS | sed -e 's|-g |-g3 -ggdb |')"

export CFLAGS="$CFLAGS -Wno-long-long"
export CFLAGS="$CFLAGS -Wno-variadic-macros"

%if 0%{?use_clang_as_cc}
export CFLAGS="$CFLAGS -Wno-gnu-statement-expression"
%endif

%if 0%{?use_gcc_strict_sanitize}
export CC="${CC} -fsanitize=address -fsanitize=undefined"
export LDFLAGS="${LDFLAGS} -pthread"
%if 0%{?use_gcc_trap_on_sanitize}
export CC="$CC -fsanitize-undefined-trap-on-error"
%endif
# Currently -fPIE binary cannot work with ASAN on kernel 4.12
# https://github.com/google/sanitizers/issues/837
export CFLAGS="$(echo $CFLAGS   | sed -e 's|-specs=[^ \t][^ \t]*hardened[^ \t][^ \t]*||g')"
export LDFLAGS="$(echo $LDFLAGS | sed -e 's|-specs=[^ \t][^ \t]*hardened[^ \t][^ \t]*||g')"
%endif

%if 0%{?use_gcc_analyzer}
export CC="${CC} -fanalyzer"
# make build log look clear
%global _smp_mflags -j1
%endif

# Show 1/100sec on blurb
export CFLAGS="$CFLAGS -DBLURB_CENTISECONDS"

CONFIG_OPTS="--prefix=%{_prefix} --with-pam --without-shadow --without-kerberos"
CONFIG_OPTS="$CONFIG_OPTS --without-setuid-hacks"
CONFIG_OPTS="$CONFIG_OPTS --with-text-file=%{default_text}"
CONFIG_OPTS="$CONFIG_OPTS --with-x-app-defaults=%{_datadir}/X11/app-defaults"
CONFIG_OPTS="$CONFIG_OPTS --disable-root-passwd"
CONFIG_OPTS="$CONFIG_OPTS --with-browser=xdg-open"

# From xscreensaver 5.12, login-manager option is on by default
# For now, let's enable it on F-14 and above
pushd TMPBINDIR
# ln -sf /bin/true gdmflexiserver
install -cpm 0755 %{SOURCE13} .
CONFIG_OPTS="$CONFIG_OPTS --with-login-manager=xscreensaver-newlogin-wrapper"
popd

# Enable extrusion on F-13 and above
# CONFIG_OPTS="$CONFIG_OPTS --with-gle" # default

# Enable account type pam validation on F-18+,
# debian bug 656766
CONFIG_OPTS="$CONFIG_OPTS --enable-pam-check-account-type"

# xscreensaver 5.30
%if 0%{?enable_animation}
CONFIG_OPTS="$CONFIG_OPTS --with-record-animation"
%endif

%if 0%{?support_setcap}
CONFIG_OPTS="$CONFIG_OPTS --with-setcap-hacks"
%endif

%if 0%{?support_systemd}
CONFIG_OPTS="$CONFIG_OPTS --with-systemd"
%endif

# This is flaky:
# CONFIG_OPTS="$CONFIG_OPTS --with-login-manager"

%if 0%{?use_clang_analyze} >= 1
#%%global _configure scan-build --use-analyzer %_bindir/clang --use-cc %_bindir/clang -v -v -v ./configure
%endif

unlink configure || :
ln -s ../configure .
%configure $CONFIG_OPTS || { cat config.log ; sleep 10 ; exit 1; }
rm -f configure

# Remove embedded build path
sed -i driver/XScreenSaver.ad -e "s|$(pwd)/TMPBINDIR/||"

%if %{update_po}
pushd po
  make generate_potfiles_in
  # The following hack still seems needed
  sed -i POTFILES.in POTFILES \
     -e '\@driver/.*\.ui@s|^\([ \t]*\)\(.*\)$|\1[type: gettext/glade]\2|'
  # Update POTFILES.in, the copy to the original directory
  cp -p POTFILES.in ../../po/
  git commit -m "POTFILES.in regenerated" -a || true
  ( cd .. ; ./config.status )

  cp -p POTFILES{.in,} ..
  make xscreensaver.pot srcdir=..
  make update-po
  rm -f ../POTFILES{.in,}
popd


( cp -p po/* ../po/)
( ( cd ../po ; git add *.po ; git commit -m "po regenerated" ) || true )
%endif

# Update po
#cp -p %{SOURCE100} po/

%if 0%{?use_clang_analyze} >= 1
%global __make scan-build  --use-analyzer %_bindir/clang --use-cc %_bindir/clang -v -v -v -o clang-analyze make
mkdir clang-analyze
%endif

BUILD_STATUS=0
%if 0%{?use_clang_analyze} < 1
make -C ../hacks/images || BUILD_STATUS=1
for dir in \
  utils driver ../hacks/images hacks/images hacks hacks/glx po
do
  %__make %{?_smp_mflags} -k \
    -C $dir \
	GMSGFMT="msgfmt --statistics" || BUILD_STATUS=1
done
%endif

# Again
%__make %{?_smp_mflags} -k || BUILD_STATUS=1
if [ $BUILD_STATUS != 0 ] ; then
	exit $BUILD_STATUS
fi

%if %{modular_conf}
# Make XScreenSavar.ad modular (bug 200881)
CONFD=xscreensaver
rm -rf $CONFD
mkdir $CONFD

# Preserve the original adfile
cp -p driver/XScreenSaver.ad $CONFD

# First split XScreenSaver.ad into 3 parts
cat driver/XScreenSaver.ad | \
   sed -n -e '1,/\*programs/p' > $CONFD/XScreenSaver.ad.header
cat driver/XScreenSaver.ad | sed -e '1,/\*programs/d' | \
   sed -n -e '1,/\\n$/p' > $CONFD/XScreenSaver.ad.hacks
cat driver/XScreenSaver.ad | sed -e '1,/\\n$/d' > $CONFD/XScreenSaver.ad.tail

# Seperate XScreenSaver.ad.hacks into each hacks
cd $CONFD
mkdir hacks.conf.d
cat XScreenSaver.ad.hacks | grep -v GL: > hacks.conf.d/xscreensaver-extras.conf
cat XScreenSaver.ad.hacks | grep    GL: > hacks.conf.d/xscreensaver-gl-extras.conf
cd ..

%endif

# test
# for now, build tests anyway (even if they are not to be installed)
make tests -C driver

%if 0%{?use_cppcheck} >= 1
cd ..
CPPCHECK_FLAGS=""
CPPCHECK_FLAGS="$CPPCHECK_FLAGS --enable=all --std=c89 -U__STRICT_ANSI__"

CPPCHECK_FLAGS="$CPPCHECK_FLAGS -I. -Iutils -Iutils/images -Idriver -Ihacks"
CPPCHECK_FLAGS="$CPPCHECK_FLAGS -I$archdir -I$archdir/driver -I$archdir/hacks"
CPPCHECK_FLAGS="$CPPCHECK_FLAGS -I$archdir/hacks/glx"
CPPCHECK_FLAGS="$CPPCHECK_FLAGS -I%{_includedir}"
# find stddef.h
GCC_HEADER_PATH=$(echo '#include <stddef.h>' | gcc -E - | sed -n -e 's|^.*"\(.*\)stddef\.h".*$|\1|p' | head -n 1)
CPPCHECK_FLAGS="$CPPCHECK_FLAGS -I$GCC_HEADER_PATH"
CPPCHECK_FLAGS="$CPPCHECK_FLAGS $(pkg-config --cflags gtk+-2.0 | sed -e 's|-pthread||')"
# C default macros
CPPCHECK_FLAGS="$CPPCHECK_FLAGS $(echo "int foo; " | gcc -dM -E - | sed -n -e "s@^\#define \([^ ][^ ]*\) 1\$@-D\1@p")"
# xscreeensaver macros
CPPCHECK_FLAGS="$CPPCHECK_FLAGS -DSTANDALONE -DHAVE_CONFIG_H -DUSE_GL"

cppcheck $CPPCHECK_FLAGS . 2>&1 | tee cppcheck-result.log
cppcheck $CPPCHECK_FLAGS --check-config . 2>&1 | tee cppcheck-path-inclusion-check.log

cd $archdir
%endif

%install
archdir=`sh ./config.guess`
cd $archdir

# Same as %%build
export PATH=/usr/bin:$PATH
pushd TMPBINDIR/
export PATH=$(pwd):$PATH
popd

rm -rf ${RPM_BUILD_ROOT}

# We have to make sure these directories exist,
# or nothing will be installed into them.
#
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d

make install_prefix=$RPM_BUILD_ROOT INSTALL="install -c -p" install

# Kill OnlyShowIn=GNOME; on F-11+ (bug 483495)
desktop-file-install --vendor "" --delete-original    \
   --dir $RPM_BUILD_ROOT%{_datadir}/applications         \
%if 0%{?fedora} < 11
   --add-only-show-in GNOME                              \
%endif
   --add-category    DesktopSettings                     \
%if 0
   --add-category X-Red-Hat-Base                         \
%else
   --remove-category Appearance                          \
   --remove-category AdvancedSettings                    \
   --remove-category Application                         \
   --remove-category Screensaver                         \
%endif
   $RPM_BUILD_ROOT%{_datadir}/applications/*.desktop

# This function prints a list of things that get installed.
# It does this by parsing the output of a dummy run of "make install".
list_files() {
   echo "%%defattr(-,root,root,-)"
   make -s install_prefix=${RPM_BUILD_ROOT} INSTALL=true "$@"  \
      | sed -e '\@gtk-update-icon-cache@d' \
      | sed -n -e 's@.* \(/[^ ]*\)$@\1@p'                      \
      | sed    -e "s@^${RPM_BUILD_ROOT}@@"                     \
               -e "s@/[a-z][a-z]*/\.\./@/@"                    \
      | sed    -e 's@\(.*/man/.*\)@%%doc \1\*@'                      \
               -e 's@\(.*/pam\.d/\)@%%config(noreplace) \1@'    \
      | sort  \
      | uniq
}

# Generate three lists of files for the three packages.
#
dd=%{_builddir}/%{name}-%{mainversion}%{?beta_ver}

# In case rpm -bi --short-circuit is tried multiple times:
rm -f $dd/*.files

(  cd hacks     ; list_files install ) >  $dd/extras.files
(  cd hacks/fonts     ; list_files install ) >>  $dd/extras.files
(  cd hacks/glx ; list_files install ) >  $dd/gl-extras.files
(  cd driver    ; list_files install ) >  $dd/base.files

%if 0%{?support_setcap} >= 1
sed -i $dd/gl-extras.files \
	-e '\@sonar$@s|^|%%attr(0755,root,root) %%caps(cap_net_raw=p)|' \
	%{nil}
%endif
# Own directory
echo "%%dir %{_datadir}/fonts/xscreensaver" >> $dd/extras.files

# Move xscreensaver-gettext-foo, xscreensaver-text to extras-base
# (bug 668427)
%if %{split_getimage}
echo "%%defattr(-,root,root,-)" >> $dd/extras-base.files
for target in \
   /xscreensaver-getimage \
   /xscreensaver-text \
   /fonts/xscreensaver \
   %{nil}
do
   grep -v $target $dd/extras.files > $dd/extras.files.new
   grep $target $dd/extras.files >> $dd/extras-base.files
   mv $dd/extras.files{.new,}
done
%endif

# Move %%{_bindir}/xscreensaver-gl-helper to gl-base
# (bug 336331).
%if %{modular_conf}
echo "%%defattr(-,root,root,-)" >> $dd/gl-base.files

grep xscreensaver-gl-visual $dd/gl-extras.files >> $dd/gl-base.files
sed -i -e '/xscreensaver-gl-visual/d' $dd/gl-extras.files
sed -i -e 's|^\(%{_mandir}.*\)$|\1*|' $dd/gl-base.files
%endif

%if %{modular_conf}
# Install update script
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
install -cpm 755 %{SOURCE10} $RPM_BUILD_ROOT%{_sbindir}
echo "%{_sbindir}/update-xscreensaver-hacks" >> $dd/base.files

# Make hack conf modular
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/xscreensaver
mkdir -p $RPM_BUILD_ROOT%{_datadir}/xscreensaver/hacks.conf.d
cp -p xscreensaver/XScreenSaver.ad* \
   $RPM_BUILD_ROOT%{_sysconfdir}/xscreensaver
cp -p xscreensaver/hacks.conf.d/xscreensaver*.conf \
   $RPM_BUILD_ROOT%{_datadir}/xscreensaver/hacks.conf.d/

for adfile in xscreensaver/XScreenSaver.ad.* ; do
   filen=`basename $adfile`
   echo "%%config(noreplace) %{_sysconfdir}/xscreensaver/$filen" >> $dd/base.files
done
echo -n "%%verify(not size md5 mtime) " >> $dd/base.files
echo "%{_sysconfdir}/xscreensaver/XScreenSaver.ad" >> \
   $dd/base.files
echo "%{_datadir}/xscreensaver/hacks.conf.d/xscreensaver-extras.conf" \
   >> $dd/extras.files
echo "%{_datadir}/xscreensaver/hacks.conf.d/xscreensaver-gl-extras.conf" \
   >> $dd/gl-extras.files

# Check symlink
rm -f $RPM_BUILD_ROOT%{_datadir}/X11/app-defaults/XScreenSaver

pushd $RPM_BUILD_ROOT%{_datadir}/X11/app-defaults
pushd ../../../..
if [ ! $(pwd) == $RPM_BUILD_ROOT ] ; then
   echo "Possibly symlink broken"
   exit 1
fi
popd
popd

ln -sf ../../../..%{_sysconfdir}/xscreensaver/XScreenSaver.ad \
   $RPM_BUILD_ROOT%{_datadir}/X11/app-defaults/XScreenSaver

%endif

# Add documents
pushd $dd &> /dev/null
for f in README* ; do
   echo "%%doc $f" >> $dd/base.files
done
popd

# Add directory
pushd $RPM_BUILD_ROOT
for dir in `find . -type d | grep xscreensaver` ; do
   echo "%%dir ${dir#.}" >> $dd/base.files
done
popd

%find_lang %{name}
cat %{name}.lang | uniq >> $dd/base.files

# Suppress rpmlint warnings
# sanitize path in script file
for f in ${RPM_BUILD_ROOT}%{_bindir}/xscreensaver-getimage-* \
   ${RPM_BUILD_ROOT}%{_libexecdir}/xscreensaver/vidwhacker \
   ${RPM_BUILD_ROOT}%{_bindir}/xscreensaver-text ; do
   if [ -f $f ] ; then
      sed -i -e 's|%{_prefix}//bin|%{_bindir}|g' $f
   fi
done

# tests
%if %{build_tests}
echo "%%defattr(-,root,root,-)" > $dd/tests.files
cd driver
for tests in `find . -name test-\* -perm -0700` ; do
   install -cpm 0755 $tests ${RPM_BUILD_ROOT}%{_libexecdir}/xscreensaver
   echo "%{_libexecdir}/xscreensaver/$tests" >> $dd/tests.files
done
cd ..
%endif

%if 0%{?use_clang_analyze} >= 1
pushd ..
rm -rf clang-analyze
mkdir -p clang-analyze/html
cp -a $archdir/clang-analyze/*/* clang-analyze/html
popd
%endif

# Install desktop application autostart stuff
# Add OnlyShowIn=GNOME (bug 517391)
# Leave autostart stuff installed (at least useful for LXDE),
# but not show them by default for all DE
# (bug 1266521) for F-27+
%if 0%{?fedora} >= 12
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/xdg/autostart
install -cpm 0755 %{SOURCE11} ${RPM_BUILD_ROOT}%{_libexecdir}/
desktop-file-install \
   --vendor "" \
   --dir ${RPM_BUILD_ROOT}%{_sysconfdir}/xdg/autostart \
%if 0%{?fedora} >= 27
   --add-only-show-in=X-NODEFAULT \
%else
   --add-only-show-in=GNOME \
%endif
   %{SOURCE12}
chmod 0644 ${RPM_BUILD_ROOT}%{_sysconfdir}/xdg/autostart/xscreensaver*.desktop

echo "%{_libexecdir}/xscreensaver-autostart" >> $dd/base.files
echo '%{_sysconfdir}/xdg/autostart/xscreensaver*.desktop' >> $dd/base.files
%endif

# Create desktop entry for gnome-screensaver
# bug 204944, 208560
create_desktop(){
   COMMAND=`cat $1 | sed -n -e 's|^<screen.*name=\"\([^ ][^ ]*\)\".*$|\1|p'`
# COMMAND must be full path (see bug 531151)
# Check if the command actually exists
   COMMAND=%{_libexecdir}/xscreensaver/$COMMAND
   if [ ! -x $RPM_BUILD_ROOT/$COMMAND ] ; then
      echo
      echo "WARNING:"
      echo "$COMMAND could not be found under $RPM_BUILD_ROOT"
      #exit 1
   fi
# NAME entry fix (bug 953558)
   NAME=`cat $1 | sed -n -e 's|^<screen.*_label=\"\([^\"][^\"]*\)\".*>.*$|\1|p'`
   ARG=`cat $1 | sed -n -e 's|^.*<command arg=\"\([^ ][^ ]*\)\".*$|\1|p'`
   ARG=$(echo "$ARG" | while read line ; do echo -n "$line " ; done)
   COMMENT="`cat $1 | sed -e '1,/_description/d' | \
     sed -e '/_description/q' | sed -e '/_description/d'`"
   COMMENT=$(echo "$COMMENT" | while read line ; do echo -n "$line " ; done)

# webcollage treatment
## changed to create wrapper script
%if 0
   if [ "x$COMMAND" = "xwebcollage" ] ; then
      ARG="$ARG -directory %{_datadir}/backgrounds/images"
   fi
%endif

   if [ "x$NAME" = "x" ] ; then NAME=$COMMAND ; fi

   rm -f $2
   echo "[Desktop Entry]" >> $2
#   echo "Encoding=UTF-8" >> $2
   echo "Name=$NAME" >> $2
   echo "Comment=$COMMENT" >> $2
   echo "TryExec=$COMMAND" >> $2
   echo "Exec=$COMMAND $ARG" >> $2
   echo "StartupNotify=false" >> $2
   echo "Type=Application" >> $2
   echo "Categories=GNOME;Screensaver;" >> $2
# Add OnlyShowIn (bug 953558)
   echo "OnlyShowIn=GNOME;MATE;" >> $2
}

cd $dd

SAVERDIR=%{_datadir}/applications/screensavers
mkdir -p ${RPM_BUILD_ROOT}${SAVERDIR}
echo "%%dir $SAVERDIR" >> base.files

for list in *extras.files ; do

   glist=gnome-$list
   rm -f $glist

   echo "%%defattr(-,root,root,-)" > $glist
##  move the owner of $SAVERDIR to -base
##   echo "%%dir $SAVERDIR" >> $glist

   set +x
   for xml in `cat $list | grep xml$` ; do
      file=${RPM_BUILD_ROOT}${xml}
      desktop=xscreensaver-`basename $file`
      desktop=${desktop%.xml}.desktop

      echo + create_desktop $file  ${RPM_BUILD_ROOT}${SAVERDIR}/$desktop
      create_desktop $file  ${RPM_BUILD_ROOT}${SAVERDIR}/$desktop
      echo ${SAVERDIR}/$desktop >> $glist
   done
   set -x
done

# Create wrapper script for webcollage to use nonet option
# by default, and rename the original webcollage
# (see bug 472061)
pushd ${RPM_BUILD_ROOT}%{_libexecdir}/%{name}
mv -f webcollage webcollage.original

cat > webcollage <<EOF
#!/bin/sh
PATH=%{_libexecdir}/%{name}:\$PATH
exec webcollage.original \\
	-directory %{_datadir}/backgrounds/images \\
	"\$@"
EOF
chmod 0755 webcollage
echo "%%{_libexecdir}/%%{name}/webcollage.original" >> \
	$dd/extras.files

# install wrapper-script for switching user
install -cpm 0755 %{SOURCE13} ${RPM_BUILD_ROOT}%{_libexecdir}/%{name}
echo "%{_libexecdir}/%{name}/xscreensaver-newlogin-wrapper" >> $dd/base.files


# Make sure all files are readable by all, and writable only by owner.
#
chmod -R a+r,u+w,og-w ${RPM_BUILD_ROOT}

%post base
%if %{modular_conf}
%{_sbindir}/update-xscreensaver-hacks
%endif

%if 0%{?fedora} >= 18
# In the case that pam setting is edited locally by sysadmin:
if ! grep -q '^account' %{_sysconfdir}/pam.d/xscreensaver
then
    echo "Warning: %{_sysconfdir}/pam.d/xscreensaver saved as %{_sysconfdir}/pam.d/xscreensaver.rpmsave"
    cp -p %{_sysconfdir}/pam.d/xscreensaver{,.rpmsave}
    PAMFILE=%{_sysconfdir}/pam.d/xscreensaver
    echo >> $PAMFILE
    echo "# Account validation" >> $PAMFILE
    echo "account include system-auth" >> $PAMFILE
fi
%endif

exit 0

%post extras
%if %{modular_conf}
%{_sbindir}/update-xscreensaver-hacks
%endif
exit 0

%postun extras
%if %{modular_conf}
%{_sbindir}/update-xscreensaver-hacks
%endif
exit 0

%post gl-extras
%if %{modular_conf}
%{_sbindir}/update-xscreensaver-hacks
%endif
exit 0

%postun gl-extras
%if %{modular_conf}
%{_sbindir}/update-xscreensaver-hacks
%endif
exit 0

%files
%defattr(-,root,root,-)

%files -f base.files base
%defattr(-,root,root,-)

%if %{build_tests}
%files -f tests.files tests
%defattr(-,root,root,-)
%endif

%if %{split_getimage}
%files -f extras-base.files extras-base
%defattr(-,root,root,-)
%endif

%files -f extras.files extras
%defattr(-,root,root,-)

%if %{modular_conf}
%files -f gl-base.files gl-base
%defattr(-,root,root,-)
%endif

%files -f gl-extras.files gl-extras
%defattr(-,root,root,-)

%files -f gnome-extras.files extras-gss
%defattr(-,root,root,-)

%files -f gnome-gl-extras.files gl-extras-gss
%defattr(-,root,root,-)

%if 0%{?use_clang_analyze} >= 1
%files clang-analyze
%doc clang-analyze/html
%endif

%if 0%{?use_cppcheck} >= 1
%files cppcheck
%doc cppcheck-*.log
%endif

%changelog
* Wed Feb 15 2023 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.06-2
- Make -base subpackage require -gl-base (debian bug 1030659)
- switch_page_cb: backport debian fix for DPMS settings issue

* Sat Jan 21 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1:6.06-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Mon Dec 12 2022 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.06-1
- Update to 6.06

* Sun Nov  6 2022 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.05-3
- Kill no longer needed workaround stuff
- hacks/fonts: fix installation on out-of-source build
- driver/Makefile.in: fix GLIB_COMPILE_RESOURCES source
- hacks/Makefile.in: fix driver/prefs.o output location

* Sat Oct 22 2022 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.05-2
- demo-Gtk.c/populate_prefs_page: use correct pointer for pref_changed_cb

* Sat Oct 22 2022 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.05-1
- Update to 6.05, now demo using GTK3

* Wed Aug 31 2022 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.04-2
- watchdog_timer: don't relaunch hacks when unblanking

* Sat Jul 23 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1:6.04-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Mon Jun  6 2022 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.04-1
- Update to 6.04

* Sun Mar 27 2022 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.03-3
- print_xinput_event: don't print raw_values (instead of
  checking if XIRawEvent.raw_values is available)

* Thu Mar 24 2022 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.03-2
- Split hacks.conf.d/xscreensaver.conf into each subpackage

* Fri Mar  4 2022 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.03-1
- Update to 6.03
- All patches sent to the upstream was merged, yeah!
- print_xinput_event: check if XIRawEvent.raw_values is available

* Sat Jan 22 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1:6.02-4.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Thu Nov  4 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.02-4
- marbling: fix signedness for x86_64 and aarch64 on vectorization
- build marbling on aarch64 again

* Mon Nov  1 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.02-3
- get_egl_config: reset loop counter with prefersGLSL option each loop
  (ref: bug 1983483)

* Sun Oct 17 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.02-2
- xscreensaver_systemd_loop: avoid use-after-free on for_each loop

* Fri Oct 15 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.02-1
- Update to 6.02
- All patches sent to the upstream was merged, yeah!
- aarch64: don't build marbling for now, does not build

* Sun Oct  3 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.01-5
- Replace two patch with ones from the upstream
  - xscreensaver-6.01-0001-main_loop-consistently-check-init-file-after-some-ac.patch
  - xscreensaver-6.01-0002-main_loop-check-init-file-saver_mode.patch
- Modify upstream patch to make force_blank_p prefer than blanking_disabled_p
- xscreesaver-text: fix uninitialize value usage for speed and update for lscpu new format

* Fri Jul 23 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1:6.01-4.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Sun Jul 18 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.01-4
- Embed SOURCE_DATE_EPOCH to version.h

* Thu Jul  8 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.01-3
- window_init: check if asterisk font is available and provide fallback character
  (bug 1980173)
- destroy_window: check ws->xftdraw to avoid nullptr dereference (bug 1966287)

* Tue Jul  6 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.01-2
- main_loop: consistently check init file after some activitity occurred
- main_loop: check init file saver_mode (bug 1978971)

* Sat Jun 19 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.01-1
- Update to 6.01

* Wed May 12 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.00-5
- input_event_to_xlib: don't call duplicate_xinput_event_p when debug mode

* Wed May  5 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.00-4
- fontglide.c: drain_input: terminate with null explicitly

* Tue May  4 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.00-3
- init_xinput: remove duplicate event for multiple screen
  patch from the upstream (bug 1954884)

* Mon May  3 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.00-2
- xscreensaver-text use en_US locale for lscpu (bug 1956089)
- dialog.c: window_init: show more version string (bug 1956262)
- Exclude xfce4-screensaver for xscreensaver-autostart (bug 1955993)
- fontglide.c: pick_font_1 exclude substitution rectagle glyph

* Fri Apr  2 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:6.00-1
- Update to 6.00

* Sat Jan 30 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.45-4
- Bump release and rebuild

* Thu Jan 28 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1:5.45-3.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Dec 28 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.45-3
- Fix up gcc -Wstringop or -Wformat-overflow warnings
- Make xscreensaver logo or ok button appear on lock screen

* Fri Dec 11 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.45-2
- test-screens.c: add skel XA_SCREENSAVER_VERSION definition

* Thu Dec 10 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.45-1
- Update to 5.45
- asm6502.c/immediate: readd free() call accidentally removed during gcc warnings fix
- beats/draw_beats: avoid integer overflow by multiplication

* Tue Nov 17 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.44-12
- Clean up gcc10 warnings, especially for -Wstringop
- Clean up some warnings by cppcheck

* Mon Nov  9 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.44-11
- Another way to make LTO happy with respecting upstream advice

* Sat Nov  7 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.44-10
- Remove unneeded undefining to make LTO happy

* Thu Oct 22 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.44-9
- Fix BR for systemd: use pkgconfig(libsystemd)

* Tue Oct 20 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.44-8
- peepers / reset_floater : fix logic for choosing color

* Wed Oct 14 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.44-6
- Install experimental wrapper script for switching user (bug 1878730)

* Sat Oct  3 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.44-5
- FuzzyFlakesFreeFlake: avoid double free on subsequent calls
  such as when ConfigureNotify event happens (bug 1884822)

* Fri Sep 25 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.44-4
- Some spec file cleanup, deleting conditions for no longer supported branches
- Use %%set_build_flags
- F-33+: enable systemd integration

* Tue Jul 28 2020 Adam Jackson <ajax@redhat.com> 1:5.44-3
- Requires appres not xorg-x11-resutils

* Thu Apr 16 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.44-2
- ya_rand_init: avoid signed integer overflow by with recent pid_max value

* Tue Mar 24 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.44-1
- Update to 5.44
- free_gibson: fix order of freeing memory

* Sat Feb  8 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.43-5
- More fix for issues detected by gcc10 sanitizer
  - send_ping(sonar-icmp.c): keep alignment for struct timeval
  - gravitywell: restict the index accessing to colors[] buffer to the valid range

* Fri Feb  7 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.43-3
- make_job (driver/subprocs.c): check is the pointer gets to the last of string buffer correctly
  (error detected by gcc10 -sanitize=address)

* Tue Jan 28 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.43-2.1
- F-32: mass rebuild

* Tue Aug 27 2019 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.43-2
- glhanoi: fix malloc size shortage (bug 1745794)

* Sat Jul 27 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:5.43-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jul 10 2019 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.43-1
- Update to 5.43

* Tue Jun 25 2019 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.42-2
- xjack: avoid freeing string literal when window is small (bug 1723461)

* Thu Jun 20 2019 Adam Jackson <ajax@redhat.com> - 1:5.42-1.3
- Drop BuildRequires: pkgconfig(xxf86misc), X servers haven't implemented that
  extension in 10+ years.

* Fri Jun 14 2019 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.42-2
- sonar: support setcap (disabled for now)

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:5.42-1.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 14 2019 Björn Esser <besser82@fedoraproject.org> - 1:5.42-1.1
- Rebuilt for libcrypt.so.2 (#1666033)

* Sun Dec 30 2018 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.42-1
- Update to 5.42
- fontglide.c: forbit C++ style comment

* Wed Aug 15 2018 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.40-1
- Update to 5.40

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:5.39-6.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jun 20 2018 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.39-6
- xscreensaver-getimage: avoid substitution to NULL pointer on GRAB_BARS mode

* Mon May 28 2018 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.39-5
- Reback to -g from -g3 to fix debuginfo generation (c.f. bug 1582631)

* Wed Apr 25 2018 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.39-4
- Actually apply patch 3903

* Mon Apr 16 2018 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.39-3
- crumbler: fix loop enclosure for calculating keys in split_chunk

* Sun Apr 15 2018 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.39-2
- crumbler: fix color overvalue when accessing colors array

* Sun Apr 15 2018 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.39-1
- Update to 5.39

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:5.38-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 30 2018 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.38-2
- esper: fix uninitialized variable

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 1:5.38-1.1
- Rebuilt for switch to libxcrypt

* Mon Dec 25 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.38-1
- Update to 5.38

* Tue Aug 15 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.37-6.1
- Actually apply Patch3704

* Mon Aug  7 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.37-6
- bsod: more stack-use-after-scope fix for utsname

* Wed Aug  2 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.37-5
- vigilance: fix which camera to pay attention on tick_camera

* Wed Aug  2 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.37-4
- bsod: fix some stack-use-after-scope issues

* Tue Aug  1 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.37-3
- store_saver_id: fix stack-use-after-scope

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:5.37-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jul 20 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.37-2
- Leave autostart stuff installed (at least useful for LXDE),
  but not show them by default for all DE
  (bug 1266521) for F-27+

* Fri Jul  7 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.37-1
- Update to 5.37

* Fri Feb 10 2017 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.36-4
- Kill gcc -Wall warnings

* Sat Oct 22 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.36-3
- hexstrut: fix one-byte-ahead access for ccolor

* Sun Oct 16 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.36-2
- splodesic: avoid using "depth" name not to make X internal collision

* Fri Oct 14 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.36-1
- Update to 5.36

* Fri Jul 15 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.35-6
- decayscreen_reshape: return immediately when not ready

* Mon Jul 11 2016 Mamoru TASAKA <mtasaka@fedoraproject.org>
- Add debugging patch: XIO: print C backtrace on error

* Fri Jun 24 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.35-5
- Update perl BR dependency per Perl#Build_Dependencies
- Use %%default_text as BR instead of fedora-release (ref: bug 1349397)

* Tue Jun  7 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.35-4
- get_best_gl_visual: waitpid for the exact gl-helper pid

* Tue Jun  7 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.35-3
- hydrostat: fix type definition in cmp_squid

* Fri Jun  3 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.35-2
- m6502: revert change on translate

* Thu May 26 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.35-1
- Update to 5.35

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:5.34-3.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sun Jan 31 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.34-3
- Apply upstream patch to fix gcc6 -Wmisleading-indentation

* Sun Jan 31 2016 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.34-2
- Kill warnings generated newly by gcc 6

* Sun Oct 25 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.34-1
- Update to 5.34

* Sat Oct 24 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.33-5.respin1
- Patch3302 revised by the upstream

* Fri Oct 23 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.33-4.respin1
- Suspend resizing when unlock (bug 1274452)

* Sun Aug 30 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.33-3.respin1
- Escape braces in xscreensaver-text to remove warning

* Mon Jul  6 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.33-2.retake1
- Upstream source refreshed, retake

* Sat Jul  4 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.33-1
- 5.33

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:5.32-12.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun Apr 19 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.32-12
- providence:update_particles: aviod one byte ahead access

* Mon Mar 23 2015 Mamoru TASAKA <mtasaka@fedoraproject.org>
- Make it sure that perl interpreter is recognized
  as /usr/bin/perl

* Sat Mar 21 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.32-11
- Fix up gdk_pixbuf BR dep, per F-23 gdk_pixbuf packaging change

* Mon Mar  9 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.32-10
- pong: adjust paddle position again on new game (bug 1199713)

* Fri Feb 27 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.32-9
- pick_font_1: rescue when XftFontOpenXlfd fails correctly
  (bug 1195437)

* Wed Feb 10 2015 Mamoru TASAKA <mtasaka@fedoraproject.org>
- Remove PATCH202 (fixed by gcc 5.0.0-0.10)

* Tue Feb 10 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.32-8
- Fix possibly wrong codes detected by cppcheck

* Tue Feb 10 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.32-7
- flush_dialog_changes_and_save: strdup for TEXT entry (bug 1190846)

* Tue Feb 10 2015 Mamoru TASAKA <mtasaka@fedoraproject.org>
- Raise debugging level to -g3

* Fri Feb  6 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.32-6
- F-22: rebuild with gcc5

* Mon Feb  2 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.32-5
- Enable double buffer on cubestorm
- Update ja.po

* Sun Feb  1 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.32-4
- Temporarily disable sse2 when gcc5 with -fsanitize=foo
- gcc5 address sanitizer fix for pick_best_gl_visual

* Sat Dec 20 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.32-3
- Enable double buffer on noof (Ubuntu bug 1390304)

* Sun Dec  7 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.32-2
- Patch from upstream for some GNOME issues with KeyPress

* Thu Nov 20 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.32-1
- Update to 5.32

* Sun Nov 16 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.31-1
- Update to 5.31

* Tue Sep 23 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.30-4
- tessellimage/tessellate: return immediately when nthreshes is zero
- Bunch of signed integer overflow fixes

* Mon Sep 15 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.30-3
- gcc49 sanitizer fix for xscreensaver-demo wrt memmove usage on de_stringify

* Sat Sep 13 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.30-2
- Some misc change on spec file for git usage

* Fri Sep 12 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.30-1
- Update to 5.30

* Sat Sep  6 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.29-3
- Remove GtkDialog:has-separator usage to suppress warning for
  xscreensaver-demo on Fedora 21 and above

* Thu Sep  4 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.29-2
- gcc49 sanitizer array elements oversize fixes
- Make parallel build actually work

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:5.29-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Jun  9 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.29-1
- Update to 5.29

* Thu Jun  5 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.28-1
- Update to 5.28

* Fri May 30 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.27-2
- Remove GLib and invalid-source-encoding warnings on clang
- Re-generate driver/XScreenSaver_ad.h correctly

* Wed May 28 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.27-1
- Update to 5.27

* Mon May  5 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.26-7
- Yet another segv fix (for extrusion), detected by
  gcc49 -fsanitize=address

* Thu May  1 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.26-6
- Yet another segv fix (for shadebobs), detected by
  gcc49 -fsanitize=address

* Wed Apr 16 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.26-5
- Yet another segv fix (for noseguy, xmatrix), detected by
  gcc49 -fsanitize=address

* Mon Apr 14 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.26-4
- Support gcc -fsanitize=address -fsanitize=undefined (disabled by default)
- And fix some errors detected by above, especially address errors
  in apple2

* Fri Apr 11 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.26-3
- F21 gcc49 rebuild

* Mon Jan 13 2014 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.26-2
- Make sync_server_dpms_settings consistent for dpms_quickoff_p option
  (bug 1047108)
- Kill memleak on goop
- Various fixes for cppcheck errors / warnings

* Tue Dec 10 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.26-1
- Update to 5.26

* Wed Nov 13 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.23-1
- Update to 5.23

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:5.22-1.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 1:5.22-1.1
- Perl 5.18 rebuild

* Wed Jul 17 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.22-1
- Update to 5.22

* Mon Jul  8 2013 Mamoru TASAKA <mtasaka@fedoraproject.org>
- Add support for Clang analyze for debugging Clang (ref: bug 982081)

* Sun Jul  7 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.21-10
- Fix memleak in on_path_p
  (Patrice Bouchand <patrice.bouchand.fedora@gmail.com>)

* Mon Jun 10 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.21-9
- Revised polyominoes patch from jwz

* Wed Jun  5 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.21-8
- Prevent apple2 segfault when receiving ConfigureNotify event
  (bug 970402)

* Thu May 30 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.21-7
- Reinitialize maze on restart, which will perhaps fix
  maze segv

* Sun May 19 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.21-6
- F-19+: Kill dependency for base on extras, gl-extras subpackage
- Fix segfault on pacman (bug 964575)

* Sun Apr 21 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.21-5
- Don't autostart xscreensaver when mate-screensaver is installed.

* Sun Apr 21 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.21-4
- Fix engine crash with one byte ahead access (bug 954115)

* Sun Apr 21 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.21-3
- Fix the iteration number for pentomino mode in polyominoes
  (bug 954077)
- Convert maxlife option from 5.20- for fireworkx (bug 953916)
- Fix broken Name entry for desktop file of GL hacks (bug 953558)
- Add OnlyShownIn entry for desktop files (bug 953558)

* Sat Feb 16 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.21-2
- Fix bumps segfault on 64bit (bug 911007)

* Thu Feb  7 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1:5.21-1
- Update to 5.21

* Mon Jan 21 2013 Adam Tkac <atkac redhat com> - 1:5.20-3.1
- rebuild due to "jpeg8-ABI" feature drop

* Tue Oct 30 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.20-3
- Prevent crash when distort receives ConfigureNotify at startup
  (bug 871433)

* Wed Oct 24 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.20-2
- Kill dependency of -gss subpackages for gnome-screensaver
  to make MATE desktop happy 

* Wed Oct 17 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.20-1
- Update to 5.20

* Sun Oct  7 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.19-6
- Use AC_SYS_LARGEFILE to detect support for -D_FILE_OFFSET_BITS=64

* Wed Oct  3 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.19-5
- May fix xscreensaver-getimage failure with BadMatch in
  XPutImage (may fix debian bug 688955)

* Fri Sep 21 2012 Mamoru Tasaka <mtasaka@fedoraproject.org>
- A bit spec file cleanup

* Mon Aug 27 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.19-4
- Remove warning from calling glLighti with float argument in engine.c

* Thu Aug 23 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.19-3
- More fix on bug 849961 (lament -no-texture)

* Wed Aug 22 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.19-2
- Fix segv on lament with -wireframe option (bug 849961)
- Fix improper and operator on flurry detected by llvm-clang

* Fri Jul 27 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.19-1
- Update to 5.19

* Fri Jul 27 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.18-3
- Build with -D_FILE_OFFSET_BITS=64 to support cifs-mounted
  filesystem for image directory (Ubuntu bug 609451)

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:5.18-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul  4 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.18-2
- Fix -verbose option usage in widwhacker as written in usage()

* Wed Jul  4 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.18-1
- Update to 5.18

* Sat Jun 30 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.17-2
- Don't call ctime in blurb in signal hander, patch by jwz

* Sat Jun 23 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.17-1
- Update to 5.17

* Thu Jun 21 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.16-1
- Update to 5.16 

* Mon Jun 18 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.15-10
- Enable account type pam validation on F-18+ (debian bug 656766)
- Try new xscreensaver-getimage-file from jwz

* Wed Jun 13 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.15-9
- And again fix Patch36 a bit...

* Wed Jun 13 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.15-8
- Fix Patch36 a bit

* Tue Jun 12 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.15-7
- xscreensaver-demo should not truncate http:// to http:/
  Also suppress warning for http:// on xscreensaver-demo
  (partial fix for bug 827771)

* Mon May  7 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.15-6
- Fix segv when quitting hack with -pair option (bug 819349)

* Fri Jan 13 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.15-5
- F-17: rebuild against fixed rpm (for perl dependency generation)

* Thu Jan  5 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.15-4
- F-17: rebuild against gcc47

* Tue Oct 18 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.15-3
- Make vidwhacker work correctly when xscreensaver-getimage-file
  returns relative path (bug 746847)

* Mon Oct  3 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.15-2
- Remove newline from xscreensaver-getimage-file result in webcollage
  to make -directory option work

* Fri Sep 30 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.15-1
- Update to 5.15
 
* Sat May 21 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.14-1
- 5.14 is released, with just fixing 5.13 DPMS issue

* Sun May 15 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.13-3
- Previous fix changed to add dpmsQuickoffEnabled option instead
  after the discussion with jwz (also see Debian bug 602157)

* Wed May 11 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.13-2
- Don't try to change DPMS state on blank-only mode startup
 (bug 702698, bug 703483)

* Tue Apr 19 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.13-1
- Update to 5.13

* Sun Apr  3 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.12-14
- Patch40 revised by jwz
- Fix segv on test-passwd
- Fix compilation error on test-xdpms

* Sun Mar 20 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1:5.12-13
- Trial patch to allow non-ascii characters on passwd window (Ubuntu bug 671923)

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:5.12-12.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jan 21 2011 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.12-12
- Make webcollage work again (for newer gdk-pixbuf)
- Fix vidwhacker also

* Tue Jan 11 2011 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.12-10
- From F-14+ (not for F-13), kill perl dependency on -base, move
  hack related files to -extras-base (bug 668427)

* Sun Jan  2 2011 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.12-9
- Fix one-byte ahead access on apple2.c (may fix 666643)

* Mon Dec 27 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.12-8
- Fix SIGFPE on wormhole with some window size (bug 665752)

* Thu Nov 11 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.12-7
- Warn (not say "Error") about missing image directory, and warn
  only once (bug 648304)

* Thu Oct 28 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.12-6
- Remove GTK warning about non-zero page-size on GtkSpinButton

* Wed Oct 13 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.12-5
- Fix the issue that flame is completely blank (bug 642651)

* Wed Oct 13 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.12-4
- Enable libgle dependent hacks on F-13+

* Wed Oct 13 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.12-3
- Kill memleak on gltext (bug 638600)

* Sun Oct 10 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp>
- F-14+: rebuild against fixed gcc

* Mon Sep 20 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.12-2
- Update Patch 31 (xscreensaver-5.12-for-now-set-lang-on-daemon-to-C.patch)
- Reduce BR using pseudo symlink

* Fri Sep 17 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.12-1
- Update to 5.12

* Mon Aug  9 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.11-9.respin1
- Fix sinc() (in ripple.c) argument when window is small
  (may fix bug 622188)

* Sun Jul 25 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.11-8.1.respin1
- And more fix for the below patch

* Sun Jul 25 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.11-8.respin1
- Fix xscreensaver-5.11-xjack-with-small-window.patch (bug 617905)

* Thu Jul  8 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.11-7.respin1
- Fix codes which contain undefined behavior, detected by gcc45

* Mon Jun 28 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.11-6.respin1
- Replace Patch32 (xscreensaver-5.11-xjack-with-small-window.patch) with the one
  revised by the upstream

* Thu Jun 24 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.11-5.respin1
- Make hacks' names in gss compat desktop files written in full path
  (ref: bug 531151)
- Update gss compat desktop creation

* Mon Jun 14 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.11-4.1.respin1
- Fix crash of xjack when window is too small (bug 603587)

* Sat Jun  5 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.11-3.respin1
- Upstream seems to have released new 5.11 tarball
  containing po/ directory, use that tarball
  (detected by Kevin's source audit)

* Sat May  1 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.11-2
- Fix crash when not using "pair" mode and when MappingNotify
  or so is received (bug 587537)

* Mon Apr 12 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.11-1
- Update to 5.11
- All patches sent to the upstream now applied in the tarball
- 2 new patches, one for autoconf, one for po
- Preserve 5.10 tarball for now for translation

* Sat Feb 27 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp>
- F-12: rebuild with newer gcc

* Fri Feb  5 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.10-6.1
- A bit more memleak fix

* Fri Feb  5 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.10-6
- Fix memleak on analogtv based hacks, especially on apple2

* Wed Feb  3 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.10-5
- Fix crash on noseguy when X resource is no longer available (bug 560614)

* Fri Dec 11 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.10-4
- Fix occasional crash on substrate (bug 545847)
- Fix initialization process on apple2, hopefully fix bug 540790??

* Thu Oct  8 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.10-2
- F-12+: Restrict Autostart effect to GNOME session only (bug 517391)
- F-12+: Use planet.fedoraproject.org for textURL (still the default textMode
  is "file", i.e. no net connection)

* Tue Sep  8 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.10-1
- Update to 5.10
- All non Fedora-specific patches applied upstream

* Thu Sep  3 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.09-1
- Update to 5.09
- Drop patches applied by upstream (1 patch still pending on upstream
  + 2 Fedora specific patches left)
- Add one patch to generate missing header files
- Suppress compilation warnings with -std=c89

* Fri Aug 28 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.08-13
- Another case of hack's crash when window size is too small
  (Ubuntu bug 418419)

* Thu Jul 30 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.08-12
- Install desktop application autostart stuff on F-12+

* Sat Jul 25 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.08-11
- Build fix for new xextproto (libXext 1.0.99.3)
- Fix for breaking strict aliasing rule
- Again change %%default_text

* Thu Jun 11 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.08-10
- Fix crash on startup when randr reports no rroi->ncrtc
  (bug 504912), patch from gentoo

* Tue Feb 24 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.08-9
- F-11: Mass rebuild

* Sun Feb 15 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.08-8
- Fix the difference of creation of desktop files for gss between
  different archs (detected by Florian Festi)

* Mon Feb  2 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.08-7
- Remove OnlyShowIn=GNOME on F-11+ (to make happy with XFCE):
  bug 483495
- Add more comments about bug reference

* Thu Jan 22 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.08-5
- Fix phosphor segv when changing window size (bug 481146)

* Tue Dec 30 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.08-4
- Fix the process of "make update-po -C po", reported by jwz

* Sun Dec 28 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.08-1
- Update to 5.08
- All non Fedora-specific patches went upstream
- Preserve all %%release string for XScreenSaver.ad, util.h

* Sat Dec 27 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.07-5
- Apply gdk trial patch from jwz (slightly modified)
- Fix warning on m6502.c

* Fri Nov 28 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.07-4
- Fix fireworkx segfault (bug 473355)

* Wed Nov 19 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.07-3
- Create wrapper script for webcollage to use nonet option
  by default, and rename the original webcollage (bug 472061)

* Fri Sep 12 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.07-2
- Update ja.po
- Fix the explanation in XScreenSaver.ad (bug 461415)

* Thu Aug 21 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.07-1
- Update to 5.07
- Fix the license tag: BSD -> MIT

* Sat Aug  9 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.06-3
- Fallback to Xinerama extension when Xrandr reports less screens
  than Xinerama
  (bug 457685: patch by jwz and Aaron Plattner <aplattner@nvidia.com>)

* Fri Jul 25 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.06-2
- Fix crash on start up in some case with dual screen
  (bug 456399: patch from jwz)

* Thu Jul 24 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp>
- Build some test binaries for debugging

* Thu Jul 17 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.06-1
- Update to 5.06

* Wed Jul  9 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.05.90.3-3
- Apply a experimental randr 1.2 patch by jwz

* Mon Jun  1 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.05-4
- Fix compilation error with GLib 2.17+

* Sun Apr  6 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.05-3
- penetrate - fallback to smaller font

* Wed Mar  5 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.05-2
- Replace addopts.patch with the patch from jwz

* Sun Mar  2 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.05-1
- Update to 5.05

* Sun Feb 10 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.04-5
- Add -Wno-overlength-strings to shut up string length warning

* Sat Feb  9 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.04-4
- Add patch to xscreensaver be happy with gcc43
- Rebuild against gcc43

* Fri Dec  7 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.04-3
- Fix desktop icon name for desktop-file-utils 0.14+ on F-9+

* Fri Nov 16 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.04-2
- Rebuild against fixed mesa for F-9 (bug 380141)

* Tue Nov 13 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.04-1
- Update to 5.04

* Thu Nov  1 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.03-14
- Patch from upstream to fix screen depth problem (also "really"
  fix bug 336331).

* Thu Oct 18 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.03-12
- Create -gl-base subpackage and split xscreensaver-gl-helper 
  into -gl-base subpackage so that external GL screensavers can
  use it (bug 336331)

* Mon Oct 15 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.03-11
- Suppress compiler warning

* Sat Oct  6 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.03-10
- Fix the maximum value on demo configuration dialog
- Change the encoding of XScreenSaver.ad and man files (bug 319101)

* Tue Oct  2 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.03-9
- Change the default browser to xdg-open
- Don't mark XScreenSaver.ad as %%config. This file is overwritten
  automatically.

* Mon Sep 24 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.03-8
- Some cleanup.

* Wed Sep 19 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.03-7
- Remove noreplace flag from XScreenSaver.ad as this is updated
  automatically.

* Sat Sep 15 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.03-6
- Fix update script to treat the ending character of conf file
  correctly.

* Sat Sep 15 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.03-5
- Add some comments on update script.

* Mon Sep  3 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.03-3
- Don't split hack part of XScreenSaver.ad into each hack piece
  and make update script allow multiple hacks in one config file
  (along with rss-glx, bug 200881)
- move hack update scripts to %%_sbindir

* Sun Sep  2 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.03-2
- Try to make XScreenSaver.ad modular (bug 200881)

* Wed Aug 29 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.03-1
- Update to 5.03

* Tue Aug 28 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.02-4
- Spec file cleanup
  - Don't use include-directory patch anymore
  - Make all xscreensaver related directories owned by -base subpackage
    because now -extras and -gl-extras subpackage require it.
  - Mark man files as %%doc explicitly, because %%_mandir is expanded
    in files list
- Fix write_long() (actually no_malloc_number_to_string())

* Wed Aug 22 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.02-3.dist.1
- Mass rebuild (buildID or binutils issue)

* Tue Aug 14 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.02-3
- Remove man6x from file entry, now included in filesystem

* Sun Aug 12 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.02-2
- Fix up desktop categories

* Sat Apr 21 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.02-1
- Update to 5.02

* Sat Feb  3 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.01-6
- Make hack packages require base package (#227017)
- Create xscreensaver metapackage

* Mon Nov 20 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.01-5
- Require xorg-x11-resutils (#216245)

* Sun Nov  5 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.01-4
- No net connection by default for webcollage (possibly fix #214095 ?)

* Fri Sep 29 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.01-3
- Fix the arguments of desktop files (#208560)

* Tue Sep 26 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.01-2
- Finally move man pages to 6x (#205796)
- Fix the ownership of directories (#187892)

* Tue Sep 19 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.01-1
- 5.01
- Revert non-passwd auth patch and disable it for now (see bug #205669)

* Sun Sep 17 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.01-0.a1.2
- 5.01a1
- Revert lang related patch (still needing some works)
- Disable small scale window (patch from upstream)
- Disable non-password authentication.

* Sun Sep 10 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-22
- Fix Patch114.

* Sun Sep 10 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-21
- Try to support non-password PAM authentication (bug #205669)

* Sat Sep  9 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-20
- Change default document.
- Again man entry fix.

* Tue Sep  5 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-19
- Create desktop files for gnome-screensaver (bug #204944)

* Mon Aug 28 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-18
- Unify locale releated patches.

* Mon Aug 28 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-17.1
- Rebuild.

* Fri Aug 18 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-17
- Very nasty segv problem was brought by me. Fixing......
 
* Thu Aug 10 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-16
- Move man entry to 6x (bug #197741)

* Fri Jul 28 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-15
- Rebuild again as fedora-release-5.91.1 is released.

* Mon Jul 17 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-14
- Correct paths to update po files properly and try re-creating po files.
- Rebuild for FC6T2 devel freeze.

* Mon Jul  3 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-13
- Fix for causing SEGV on exit about petri, squiral (total: 22 hacks)
  I hope this will finally fix all hacks' problems.

* Sun Jul  2 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-12
- Fix other (extras, gl-extras) hacks (total: 21 hacks).
- Make sure the subprocess xscreensaver-getimage is properly
  killed by parent hack process.

* Fri Jun 30 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-11
- Fix interaggregate segv.

* Thu Jun 29 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-10
- Fix xscreensaver-extras hacks which cause SEGV or SIGFPE.

* Tue Jun 27 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-9
- Don't make xscreensaver-base require htmlview.
- Update ja.po again.
- Fix noseguy not to eat cpu when geometry is too small.

* Fri Jun 23 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-8
- Spec file script change.
- Add libtool to BuildRequires.

* Thu Jun 15 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-7
- Change timestamps.
- Forcely replace the default text till the release version of fedora-release
  formally changes.

* Sat Jun 10 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-6.1
- Fix the requirement for rebuilding to meet the demand
  from current mock.

* Wed Jun  7 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-6
- Another fixes of config files for ifsmap as reported to jwz 
  livejournal page.
- Update Japanese translation.
- Locale fix for xscreensaver-text.

* Thu Jun  1 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-5
- Disable (not remove) some hacks by default according to 4.24 behavior.
- XML file fix for slidescreen.

* Thu Jun  1 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-4
- Rewrite the patch for decimal separator as discussed with jwz.
- Change defaults not by patch but by function.

* Wed May 31 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-3
- Fix browser option patch.

* Wed May 31 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-2
- Change the default text.
- Rewrite root passwd patch.
- Add browser option to configure.
- Fix requirement about desktop-backgrounds-basic.
- Fix decimal separator problem reported by upstream.

* Fri May 26 2006 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1:5.00-1
- Update to 5.00 .
- Switch to extras, don't remove anything.

* Fri Mar 24 2006 Ray Strode <rstrode@redhat.com> - 1:4.24-2
- add patch from jwz to reap zombie processes (bug 185833)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1:4.24-1.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1:4.23-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Jan 13 2006 Ray Strode <rstrode@redhat.com> 1:4.23-1
- update to 4.23
- add a BuildRequires on imake (spotted by Mamoru Tasaka)
- add a lot of patches and fixes from Mamoru Tasaka

* Sat Dec 17 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Mon Dec  5 2005 Ray Strode <rstrode@redhat.com> 1:4.22-21
- Update list_files function to fix ownership issues.
  Patch from Mamoru Tasaka (mtasaka@ioa.s.u-tokyo.ac.jp) (bug 161728).

* Tue Nov  1 2005 Ray Strode <rstrode@redhat.com> 1:4.22-20
- Switch requires to modular X

* Thu Oct 13 2005 Tomas Mraz <tmraz@redhat.com> 1:4.22-19
- use include instead of pam_stack in pam config

* Wed Sep 28 2005 Ray Strode <rstrode@redhat.com> 1:4.22-18
- accept zero timeout values for suspend and off.
  Patch from Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp>
  (bug 157501). 

* Fri Sep 23 2005 Ray Strode <rstrode@redhat.com> 1:4.22-17
- remove explicit dependency on xscreensaver-base for 
  extras and gl-extras packages

* Fri Sep 16 2005 Ray Strode <rstrode@redhat.com> 1:4.22-16
- don't allow root to authenticate lock dialog when selinux
  is enabled (bug 157014).

* Fri Sep  9 2005 Ray Strode <rstrode@redhat.com> 1:4.22-15
- take BSOD out of the default random list (bug 105388).

* Thu Sep 08 2005 Florian La Roche <laroche@redhat.com>
- add version-release to the Provides:

* Wed Sep  7 2005 Ray Strode <rstrode@redhat.com> 1:4.22-13
- Patch from Mamoru Tasaka to improve man page handling
  (bug 167708).

* Tue Sep  6 2005 Ray Strode <rstrode@redhat.com> 1:4.22-12
- remove density option from squiral screensaver,
  Patch from Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp>
  (bug 167374).

* Wed Aug 31 2005 Ray Strode <rstrode@redhat.com> 1:4.22-11
- ignore unprintable characters in password dialog (bug 135966).

* Thu Aug 25 2005 Ray Strode <rstrode@redhat.com> 1:4.22-10
- Move man pages to section 6 (bug 166441). 

* Wed Aug 24 2005 Ray Strode <rstrode@redhat.com> 1:4.22-9
- The only legitimate way to call realpath is with NULL 
  buffer (bug 165270).

* Fri Aug 19 2005 Ray Strode <rstrode@redhat.com> 1:4.22-8
- Don't try to use an invalid tree iterator (bug 166299)

* Tue Aug 16 2005 Warren Togami <wtogami@redhat.com> - 1:4.22-7
- rebuild for new cairo

* Wed Aug 10 2005 Ray Strode <rstrode@redhat.com> 1:4.22-6
- Don't call printf in signal handler (might fix 126428)

* Wed Aug  3 2005 Ray Strode <rstrode@redhat.com> 1:4.22-5
- Update to xscreensaver 4.22.

* Sun Jun 19 2005 Ray Strode <rstrode@redhat.com> 1:4.21-5
- Add build requires for desktop-file-utils (bug 160980). 

* Wed May 11 2005 Ray Strode <rstrode@redhat.com> 1:4.21-4
- Allow configuration gui to support hacks with absolute paths
  (bug 157417). 

* Mon May 09 2005 Ray Strode <rstrode@redhat.com> 1:4.21-3
- Use @libexecdir@/xscreensaver instead of @HACKDIR@ in
  default configuration file so that the path gets expanded
  fully (bug 156906).

* Tue May 03 2005 Ray Strode <rstrode@redhat.com> 1:4.21-2
- Use absolute filenames for screenhacks so we don't pull
  in screenhacks from PATH (bug 151677).
- Don't try to ping in sonar screensaver (bug 139692).

* Sun Mar 20 2005 Ray Strode <rstrode@redhat.com> 1:4.21-1
- Update to xscreensaver-4.21.
- Update spec file to better match new upstream spec file.

* Fri Feb 25 2005 Nalin Dahyabhai <nalin@redhat.com> 1:4.18-19
- We don't patch configure.in, so we don't need to run 'autoconf'.
- Add --without-kerberos to skip built-in Kerberos password verification, so
  that we'll always go through PAM (fixes 149731).

* Mon Feb 21 2005 Ray Strode <rstrode@redhat.com> 1:4.18-18
- Install desktop files to /usr/share/applications instead of
  /usr/share/control-center-2.0 (should fix bug 149229).

* Thu Jan  6 2005 Ray Strode <rstrode@redhat.com> 1:4.18-17
- Change lock dialog instructions to only ask for password
  and not username.

* Tue Jan  4 2005 Ray Strode <rstrode@redhat.com> 1:4.18-16
- Add patch to spec file to change defaults

* Tue Jan  4 2005 Ray Strode <rstrode@redhat.com> 1:4.18-15
- Remove xscreensaver-config-tool after some discussions with
  jwz.
- Take out some additional screensavers

* Wed Dec  1 2004 Ray Strode <rstrode@redhat.com> 1:4.18-14
- Add utility xscreensaver-config-tool to make changing settings
  easier (replaces the short lived xscreensaver-register-hack
  program).  Use xscreensaver-config-tool to set default settings
  instead of using patches. 
- Split up xscreensaver (fixes 121693).
- Make preferences dialog slightly more pretty
- Make lock dialog slightly more pretty

* Fri Nov 26 2004 Than Ngo <than@redhat.com> 1:4.18-13
- add patch to fix vroot bug and make xscreensaver working in KDE again.
- get rid of webcollage, which often download porn images
 
* Wed Nov 10 2004 Ray Strode <rstrode@redhat.com> 1:4.18-11
- Add xscreensaver-register-hack program to make
  installing and uninstalling screensavers easier
  (working toward fixing bug 121693 [split up screensaver])

* Wed Nov 10 2004 Ray Strode <rstrode@redhat.com> 1:4.18-10
- Get rid of unnecessary xloadimage requirement
  (bug 100641)

* Wed Nov 10 2004 Ray Strode <rstrode@redhat.com> 1:4.18-9
- Call pam_acct_mgmt() (might fix bug 137195) 

* Tue Nov 9 2004 Ray Strode <rstrode@redhat.com> 1:4.18-8
- Give vidwhacker screensaver working defaults
  (bug 64518)

* Tue Nov 9 2004 Ray Strode <rstrode@redhat.com> 1:4.18-7
- Get rid of old crufty %%{_datadir}/control-center/ tree
  (bug 114692)

* Wed Nov 3 2004 Ray Strode <rstrode@redhat.com> 1:4.18-6
- rebuild for rawhide

* Wed Nov 3 2004 Ray Strode <rstrode@redhat.com> 1:4.18-5
- Don't allow screensavers access to desktop images by default (bug #126809)
- Lock screen by default (bug #126809)

* Tue Oct 19 2004  <krh@redhat.com> 4.18-4
- Add xscreensaver-4.18-stuff-piecewise-leak.patch to stop piecewise
  from leaking (#135164).

* Wed Sep 1 2004 Ray Strode <rstrode@redhat.com> 4.18-3
- remove superfluous line in the spec file

* Wed Sep 1 2004 Ray Strode <rstrode@redhat.com> 4.18-2
- blank the screen by default

* Tue Aug 24 2004 Ray Strode <rstrode@redhat.com> 4.18-1
- update to 4.18 (fixes bug 87745).

* Sat Aug 14 2004 Ray Strode <rstrode@redhat.com> 4.16-4
- change titles of questionably named bar codes
  (fixes bug 129929).

* Fri Aug 6 2004 Ray Strode <rstrode@redhat.com> 4.16-3
- change titles of questionably named shape formations
  (fixes bug 129335).

* Wed Jun 23 2004 Ray Strode <rstrode@redhat.com> 4.16-2
- use htmlview for browsing help.

* Mon Jun 21 2004 Ray Strode <rstrode@redhat.com> 4.16-1
- update to 4.16.  Use desktop-file-install for desktop file.

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed May  5 2004 Bill Nottingham <notting@redhat.com> 4.14-5
- config tweaks

* Wed Mar 31 2004 Karsten Hopp <karsten@redhat.de> 4.14-4 
- fix fortune stand-in (#115369)

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Oct 27 2003 Bill Nottingham <notting@redhat,com> 1:4.14-1
- update to 4.14

* Tue Oct  7 2003 Bill Nottingham <notting@redhat.com> 1:4.13-1
- take out flag-with-logo, don't require redhat-logos (#106046)
- update to 4.13

* Wed Aug 27 2003 Bill Nottingham <notting@redhat.com> 1:4.12-1
- update to 4.12 (fixes #101920)
- re-add BSOD to the random list

* Tue Jun 24 2003 Bill Nottingham <notting@redhat.com> 1:4.11-1
- update to 4.11

* Fri Jun 13 2003 Bill Nottingham <notting@redhat.com> 1:4.10-3
- fix some 64-bit arches (#97359)

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed May 28 2003 Bill Nottingham <notting@redhat.com> 1:4.10-1
- update to 4.10

* Thu Mar 20 2003 Bill Nottingham <notting@redhat.com> 1:4.09-1
- update to 4.09, now with bouncing cows

* Mon Feb 10 2003 Bill Nottingham <notting@redhat.com> 1:4.07-2
- oops, xloadimage *is* needed (#83676)

* Thu Feb  6 2003 Bill Nottingham <notting@redhat.com> 1:4.07-1
- update to 4.07, fixes #76276, #75574

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Fri Nov 29 2002 Tim Powers <timp@redhat.com> 1:4.06-4
- call autoconf instead of autoconf-2.53

* Mon Nov 11 2002 Bill Nottingham <notting@redhat.com> 4.06-3
- put glade tweaks back in
- switch pam package to not specify directories, to work on multilib
  arches

* Fri Nov  8 2002 Nalin Dahyabhai <nalin@redhat.com> 4.06-1
- add a BuildPrereq on bc, which configure requires
- replace use of fortune with an innocuous-and-editable stand-in script in
  %%{stand_in_path}
- define FORTUNE_PROGRAM at compile-time to force apps to use what's specified
  even if it doesn't happen to be installed at compile-time

* Sun Sep  2 2002 Bill Nottingham <notting@redhat.com> 4.05-6
- fix typo (#73246)

* Wed Aug 28 2002 Bill Nottingham <notting@redhat.com> 4.05-5
- revert to non-gtk unlock dialog
- fix translations

* Mon Aug 12 2002 Bill Nottingham <notting@redhat.com> 4.05-4
- twiddle titlebar (#67844)
- fix extraneous text (#70975)
- tweak desktop entry (#69502)

* Fri Aug 9 2002 Yu Shao <yshao@redhat.com> 4.05-3
- use GTK_IM_MODULE=gtk-im-context-simple in lock widget
- to avoid CJK IM weirdness (#70655, #68216)
- xscreensaver-rh-imcjk.patch

* Wed Jul 17 2002 Elliot Lee <sopwith@redhat.com> 4.05-2
- Add fortune-mod to buildprereq to make beehive happy
- Fix find_lang usage - install translations properly by specifying datadir

* Tue Jun 11 2002 Bill Nottingham <notting@redhat.com> 4.05-1
- update to 4.05
- use gtk2 lock widget (<jacob@ximian.com>)
- some Red Hat-ifications
- fix critical (#63916)

* Mon Jun 10 2002 Bill Nottingham <notting@redhat.com> 4.04-2
- remove no longer needed xloadimage dependency

* Mon Jun  3 2002 Bill Nottingham <notting@redhat.com> 4.04-1
- update to 4.04, gtk2 property dialog is now mainline

* Thu May 16 2002 Bill Nottingham <notting@redhat.com> 4.03-1
- update to 4.03
- use gtk2 properties dialog

* Thu Mar 14 2002 Bill Nottingham <notting@redhat.com> 4.01-2
- don't show screensavers that aren't available

* Sun Feb 24 2002 Bill Nottingham <notting@redhat.com>
- update to 4.01

* Mon Feb 11 2002 Bill Nottingham <notting@redhat.com>
- update to 4.00

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Aug 23 2001 Bill Nottingham <notting@redhat.com>
- fix segfault on ia64 (#52336)

* Thu Aug  9 2001 Bill Nottingham <notting@redhat.com>
- never mind, back to 3.33 (wheeee)
- hack window-id back in for the time being
- disable memlimit so GL works

* Mon Jul 23 2001 Bill Nottingham <notting@redhat.com>
- oops, back to 3.32 for now
- remove optflags override (oops)
- add pam-devel buildprereq

* Mon Jul 16 2001 Bill Nottingham <notting@redhat.com>
- update to 3.33, fix broken last build
- fix build weirdness on some package sets (#48905)
- don't document non-existent options for forest (#49139)

* Sun Jun 24 2001 Elliot Lee <sopwith@redhat.com>
- Bump release + rebuild.

* Tue May 22 2001 Havoc Pennington <hp@redhat.com>
- putting in tree for David 

* Tue May 22 2001 David Sainty <dsainty@redhat.com>
- added DPMS options to command line help

* Sun Apr 22 2001 Bill Nottingham <notting@redhat.com>
- update to 3.32
- add patch to specify DPMS settings on the command line

* Wed Apr 11 2001 Bill Nottingham <notting@redhat.com>
- update to 3.31

* Wed Apr  4 2001 Bill Nottingham <notting@redhat.com>
- fix extrusion exclusion (#34742)

* Tue Apr  3 2001 Bill Nottingham <notting@redhat.com>
- disable GL screensavers by default (bleah)

* Mon Feb 19 2001 Bill Nottingham <notting@redhat.com>
- update to 3.29 (#27437)

* Tue Jan 23 2001 Bill Nottingham <notting@redhat.com>
- update to 3.27

* Fri Dec 01 2000 Bill Nottingham <notting@redhat.com>
- rebuild because of broken fileutils

* Fri Nov 10 2000 Bill Nottingham <notting@redhat.com>
- 3.26

* Fri Aug 11 2000 Jonathan Blandford <jrb@redhat.com>
- Up Epoch and release

* Wed Jul 26 2000 Bill Nottingham <notting@redhat.com>
- hey, vidmode works again

* Fri Jul 21 2000 Bill Nottingham <notting@redhat.com>
- update to 3.25

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Sat Jun 17 2000 Bill Nottingham <notting@redhat.com>
- xscreensaver.kss is not a %%config file.

* Sun Jun 11 2000 Bill Nottingham <notting@redhat.com>
- tweak kss module (#11872)

* Thu Jun  1 2000 Nalin Dahyabhai <nalin@redhat.com>
- modify PAM configuration to use system-auth

* Thu May 18 2000 Preston Brown <pbrown@redhat.com>
- added Red Hat screensaver (waving flag has logo now).

* Fri May  5 2000 Bill Nottingham <notting@redhat.com>
- tweaks for ia64

* Mon Apr 10 2000 Bill Nottingham <notting@redhat.com>
- turn off xf86vidmode ext, so that binaries built against XFree86 4.0
  work on 3.x servers

* Wed Apr  5 2000 Bill Nottingham <notting@redhat.com>
- turn off gnome support for now

* Mon Apr  3 2000 Bill Nottingham <notting@redhat.com>
- update to 3.24

* Wed Feb 09 2000 Preston Brown <pbrown@redhat.com>
- wmconfig entry gone.

* Mon Jan 31 2000 Bill Nottingham <notting@redhat.com>
- update to 3.23

* Fri Jan 14 2000 Bill Nottingham <notting@redhat.com>
- rebuild to fix GL depdencies

* Tue Dec 14 1999 Bill Nottingham <notting@redhat.com>
- everyone in GL
- single package again

* Fri Dec 10 1999 Bill Nottingham <notting@redhat.com>
- update to 3.22
- turn off xf86vmode on alpha

* Tue Dec  7 1999 Bill Nottingham <notting@redhat.com>
- mmm... hardware accelerated GL on i386. :) :)

* Mon Nov 22 1999 Bill Nottingham <notting@redhat.com>
- 3.21
- use shm on alpha, let's see what breaks

* Tue Nov 16 1999 Bill Nottingham <notting@redhat.com>
- update to 3.20

* Wed Nov  3 1999 Bill Nottingham <notting@redhat.com>
- update to 3.19

* Thu Oct 14 1999 Bill Nottingham <notting@redhat.com>
- update to 3.18

* Sat Sep 25 1999 Bill Nottingham <notting@redhat.com>
- add a '-oneshot' single time lock option.

* Mon Sep 20 1999 Bill Nottingham <notting@redhat.com>
- take webcollage out of random list (for people who pay for bandwidth)

* Fri Sep 10 1999 Bill Nottingham <notting@redhat.com>
- patch webcollage to use xloadimage
- in the random list, run petri with -size 2 to save memory
- extend RPM silliness to man pages, too.

* Mon Jul 19 1999 Bill Nottingham <notting@redhat.com>
- update to 3.17
- add a little RPM silliness to package GL stuff if it's built

* Thu Jun 24 1999 Bill Nottingham <notting@redhat.com>
- update to 3.16

* Mon May 10 1999 Bill Nottingham <notting@redhat.com>
- update to 3.12

* Tue May  4 1999 Bill Nottingham <notting@redhat.com>
- remove security problem introduced earlier

* Wed Apr 28 1999 Bill Nottingham <notting@redhat.com>
- update to 3.10

* Thu Apr 15 1999 Bill Nottingham <notting@redhat.com>
- kill setuid the Right Way(tm)

* Mon Apr 12 1999 Bill Nottingham <notting@redhat.com>
- fix xflame on alpha

* Mon Apr 12 1999 Preston Brown <pbrown@redhat.com>
- upgrade to 3.09, fixes vmware interaction problems.

* Mon Apr  5 1999 Bill Nottingham <notting@redhat.com>
- remove setuid bit. Really. I mean it.

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 3)

* Fri Mar 19 1999 Bill Nottingham <notting@redhat.com>
- kill setuid, since pam works OK

* Tue Mar 16 1999 Bill Nottingham <notting@redhat.com>
- update to 3.08

* Wed Feb 24 1999 Bill Nottingham <notting@redhat.com>
- wmconfig returns, and no one is safe...

* Tue Feb 23 1999 Bill Nottingham <notting@redhat.com>
- remove bsod from random list because it's confusing people???? *sigh*

* Tue Jan 12 1999 Cristian Gafton <gafton@redhat.com>
- call libtoolize to get it to compile cleanely on the arm

* Tue Jan  5 1999 Bill Nottingham <notting@redhat.com>
- update to 3.07

* Mon Nov 23 1998 Bill Nottingham <notting@redhat.com>
- update to 3.06

* Tue Nov 17 1998 Bill Nottingham <notting@redhat.com>
- update to 3.04

* Thu Nov 12 1998 Bill Nottingham <notting@redhat.com>
- update to 3.02
- PAMify

* Tue Oct 13 1998 Cristian Gafton <gafton@redhat.com>
- take out Noseguy module b/c of possible TMv
- install modules in /usr/X11R6/lib/xscreensaver
- don't compile support for xshm on the alpha
- properly buildrooted
- updated to version 2.34

* Fri Aug  7 1998 Bill Nottingham <notting@redhat.com>
- update to 2.27

* Wed Jun 10 1998 Prospector System <bugs@redhat.com>
- translations modified for de

* Mon Jun 08 1998 Erik Troan <ewt@redhat.com>
- added fix for argv0 buffer overflow

* Fri Apr 24 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Sat Apr 11 1998 Donnie Barnes <djb@redhat.com>
- updated from 2.10 to 2.16
- added buildroot

* Wed Oct 25 1997 Marc Ewing <marc@redhat.com>
- wmconfig

* Thu Oct 23 1997 Marc Ewing <marc@redhat.com>
- new version, configure

* Fri Aug 22 1997 Erik Troan <ewt@redhat.com>
- built against glibc

