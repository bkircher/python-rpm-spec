# Pass --without docs to rpmbuild if you don't want the documentation

%global gitexecdir          %{_libexecdir}/git-core

# Settings for F-19+ and EL-7+
%if 0%{?fedora} || 0%{?rhel} >= 7
%global bashcomp_pkgconfig  1
%global bashcompdir         %(pkg-config --variable=completionsdir bash-completion 2>/dev/null)
%global bashcomproot        %(dirname %{bashcompdir} 2>/dev/null)
%global libsecret           1
%global use_new_rpm_filters 1
%global use_systemd         1
%else
%global bashcomp_pkgconfig  0
%global bashcompdir         %{_sysconfdir}/bash_completion.d
%global bashcomproot        %{bashcompdir}
%global libsecret           0
%global use_new_rpm_filters 0
%global use_systemd         0
%endif

# gnome-keyring is deprecated, however someone would like
# to use it on older fedora instead of libsecret. So that's
# why this ugly solution
# TODO: we should maybe update conditions according to supported systems
%if ( 0%{?fedora} && 0%{?fedora} < 26 ) || 0%{?rhel} == 7
%global gnome_keyring       1
%else
%global gnome_keyring       0
%endif

# Settings for EL <= 7
%if 0%{?rhel} && 0%{?rhel} <= 7
%{!?__global_ldflags: %global __global_ldflags -Wl,-z,relro}
%endif

# fallback for F17- && RHEL6-
%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

%if 0%{?fedora} && 0%{?fedora} >= 25
%global test_links 1
%else
%global test_links 0
%endif

# Allow tests to run in parallel.  Disabled by default due to unresolved
# failures when building in koji.  Enabling it speeds up the test suite quite a
# bit though.  The -O (--output-sync) option requires make > 4.0, which is not
# available on EL <= 7.  Without it, running the tests in parallel causes the
# output to be rather unweildy, so restrict parallel tests to Fedora.
#
# Pass "--with parallel_tests" or "--define 'parallel_tests 1'" to
# rpmbuild/mock.
%bcond_with parallel_tests
%if %{with parallel_tests} && 0%{?fedora}
%global make_test_opts -O %{?_smp_mflags}
%endif

# Define for release candidates
#global rcrev   .rc0

Name:           git
Version:        2.15.1
Release:        2%{?rcrev}%{?dist}
Summary:        Fast Version Control System
License:        GPLv2
Group:          Development/Tools
URL:            https://git-scm.com/
Source0:        https://www.kernel.org/pub/software/scm/git/%{?rcrev:testing/}%{name}-%{version}%{?rcrev}.tar.xz
Source1:        https://www.kernel.org/pub/software/scm/git/%{?rcrev:testing/}%{name}-%{version}%{?rcrev}.tar.sign

# Junio C Hamano's key is used to sign git releases, it can be found in the
# junio-gpg-pub tag within git.
#
# (Note that the tagged blob in git contains a version of the key with an
# expired signing subkey.  The subkey expiration has been extended on the
# public keyservers, but the blob in git has not been updated.)
#
# https://git.kernel.org/cgit/git/git.git/tag/?h=junio-gpg-pub
# https://git.kernel.org/cgit/git/git.git/blob/?h=junio-gpg-pub&id=7214aea37915ee2c4f6369eb9dea520aec7d855b
Source9:        gpgkey-junio.asc

# Local sources begin at 10 to allow for additional future upstream sources
Source10:       git-init.el
Source11:       git.xinetd.in
Source12:       git.conf.httpd
Source13:       git-gui.desktop
Source14:       gitweb.conf.in
Source15:       git@.service
Source16:       git.socket
Patch0:         git-1.8-gitweb-home-link.patch
# https://bugzilla.redhat.com/490602
Patch1:         git-cvsimport-Ignore-cvsps-2.2b1-Branches-output.patch

# https://bugzilla.redhat.com/1510455 (CVE-2017-15298)
# https://github.com/git/git/commit/a937b37e76
Patch2:         0001-revision-quit-pruning-diff-more-quickly-when-possibl.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if ! 0%{?_without_docs}
BuildRequires:  asciidoc >= 8.4.1
BuildRequires:  xmlto
%if %{test_links}
BuildRequires:  linkchecker
%endif
%endif
BuildRequires:  desktop-file-utils
BuildRequires:  emacs
BuildRequires:  expat-devel
BuildRequires:  gettext
BuildRequires:  gnupg2
BuildRequires:  libcurl-devel
%if %{libsecret}
BuildRequires:  libsecret-devel
%endif
BuildRequires:  pcre2-devel
%if 0%{?fedora}
BuildRequires:  perl-generators
%endif
BuildRequires:  perl(Test)
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel >= 1.2
BuildRequires:  tcl
BuildRequires:  tk
%if %{bashcomp_pkgconfig}
BuildRequires:  pkgconfig(bash-completion)
%endif
%if %{use_systemd}
# For macros
BuildRequires:  systemd
%endif

# Test suite requirements
%if 0%{?fedora} && 0%{?fedora} >= 27
# Needed by t5540-http-push-webdav.sh
BuildRequires: apr-util-bdb
%endif
BuildRequires:  cvs
BuildRequires:  cvsps
BuildRequires:  gnupg
%if 0%{?fedora} || ( 0%{?rhel} && 0%{?rhel} == 7 && "%{_arch}" != "ppc64" )
BuildRequires:  highlight
%endif
BuildRequires:  httpd
%if 0%{?fedora}
BuildRequires:  jgit
%endif
BuildRequires:  pcre
BuildRequires:  perl(CGI)
BuildRequires:  perl(CGI::Carp)
BuildRequires:  perl(CGI::Util)
BuildRequires:  perl(DBD::SQLite)
BuildRequires:  perl(Digest::MD5)
BuildRequires:  perl(IO::Pty)
BuildRequires:  perl(Mail::Address)
BuildRequires:  perl(Memoize)
BuildRequires:  perl(Test::More)
BuildRequires:  perl(Time::HiRes)
BuildRequires:  subversion
BuildRequires:  subversion-perl
BuildRequires:  time

Requires:       git-core = %{version}-%{release}
Requires:       git-core-doc = %{version}-%{release}
Requires:       perl(Error)
%if ! %{defined perl_bootstrap}
Requires:       perl(Term::ReadKey)
%endif
Requires:       perl-Git = %{version}-%{release}

%if 0%{?fedora} || 0%{?rhel} >= 7
Requires:       emacs-filesystem >= %{_emacs_version}
# These can be removed in Fedora 26
Obsoletes:      emacs-git <= 2.4.5
Obsoletes:      emacs-git-el <= 2.4.5
Provides:       emacs-git = %{version}-%{release}
Provides:       emacs-git-el = %{version}-%{release}
%endif

%description
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

The git rpm installs common set of tools which are usually using with
small amount of dependencies. To install all git packages, including
tools for integrating with other SCMs, install the git-all meta-package.

%package all
Summary:        Meta-package to pull in all git tools
Group:          Development/Tools
BuildArch:      noarch
Requires:       git = %{version}-%{release}
%if %{gnome_keyring}
Requires:       git-gnome-keyring = %{version}-%{release}
%endif
Requires:       git-cvs = %{version}-%{release}
Requires:       git-email = %{version}-%{release}
Requires:       git-gui = %{version}-%{release}
Requires:       git-svn = %{version}-%{release}
Requires:       git-p4 = %{version}-%{release}
Requires:       gitk = %{version}-%{release}
Requires:       perl-Git = %{version}-%{release}
%if ! %{defined perl_bootstrap}
Requires:       perl(Term::ReadKey)
%endif
%if 0%{?rhel} && 0%{?rhel} <= 6
Requires:       emacs-git = %{version}-%{release}
%endif
%description all
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

This is a dummy package which brings in all subpackages.

%package core
Summary:        Core package of git with minimal functionality
Group:          Development/Tools
Requires:       less
Requires:       openssh-clients
Requires:       zlib >= 1.2
%description core
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

The git-core rpm installs really the core tools with minimal
dependencies. Install git package for common set of tools.
To install all git packages, including tools for integrating with
other SCMs, install the git-all meta-package.

%package core-doc
Summary:        Documentation files for git-core
Group:          Development/Tools
Requires:       git-core = %{version}-%{release}
%description core-doc
Documentation files for git-core package including man pages.

%package daemon
Summary:        Git protocol daemon
Group:          Development/Tools
Requires:       git = %{version}-%{release}
%if %{use_systemd}
Requires:       systemd
Requires(post): systemd
Requires(preun):  systemd
Requires(postun): systemd
%else
Requires:       xinetd
%endif
%description daemon
The git daemon for supporting git:// access to git repositories

%package -n gitweb
Summary:        Simple web interface to git repositories
Group:          Development/Tools
BuildArch:      noarch
Requires:       git = %{version}-%{release}
%description -n gitweb
%{summary}.

%package p4
Summary:        Git tools for working with Perforce depots
Group:          Development/Tools
BuildArch:      noarch
BuildRequires:  python2-devel
Requires:       git = %{version}-%{release}
%description p4
%{summary}.

%package svn
Summary:        Git tools for interacting with Subversion repositories
Group:          Development/Tools
Requires:       git = %{version}-%{release}, subversion
Requires:       perl(Digest::MD5)
%if ! %{defined perl_bootstrap}
Requires:       perl(Term::ReadKey)
%endif
%description svn
%{summary}.

%package cvs
Summary:        Git tools for importing CVS repositories
Group:          Development/Tools
BuildArch:      noarch
Requires:       git = %{version}-%{release}, cvs
Requires:       cvsps
Requires:       perl(DBD::SQLite)
Requires:       perl(Git)
%description cvs
%{summary}.

%package email
Summary:        Git tools for sending patches via email
Group:          Development/Tools
BuildArch:      noarch
Requires:       git = %{version}-%{release}, perl-Git = %{version}-%{release}
Requires:       perl(Authen::SASL)
Requires:       perl(Net::SMTP::SSL)
Requires:       perl(Git)
%description email
%{summary}.

%package gui
Summary:        Graphical interface to Git
Group:          Development/Tools
BuildArch:      noarch
Requires:       git = %{version}-%{release}, tk >= 8.4
Requires:       gitk = %{version}-%{release}
%description gui
%{summary}.

%package -n gitk
Summary:        Git repository browser
Group:          Development/Tools
BuildArch:      noarch
Requires:       git = %{version}-%{release}, tk >= 8.4
%description -n gitk
%{summary}.

%package -n perl-Git
Summary:        Perl interface to Git
Group:          Development/Libraries
BuildArch:      noarch
Requires:       git = %{version}-%{release}
BuildRequires:  perl(Error), perl(ExtUtils::MakeMaker)
Requires:       perl(Error)
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
%description -n perl-Git
%{summary}.

%package -n perl-Git-SVN
Summary:        Perl interface to Git::SVN
Group:          Development/Libraries
BuildArch:      noarch
Requires:       git = %{version}-%{release}
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
%description -n perl-Git-SVN
%{summary}.

%if 0%{?rhel} && 0%{?rhel} <= 6
%package -n emacs-git
Summary:        Git version control system support for Emacs
Group:          Applications/Editors
Requires:       git = %{version}-%{release}
BuildArch:      noarch
Requires:       emacs(bin) >= %{_emacs_version}
%description -n emacs-git
%{summary}.

%package -n emacs-git-el
Summary:        Elisp source files for git version control system support for Emacs
Group:          Applications/Editors
BuildArch:      noarch
Requires:       emacs-git = %{version}-%{release}
%description -n emacs-git-el
%{summary}.
%endif

%if %{gnome_keyring}
%package gnome-keyring
Summary:        Git helper for accessing credentials via gnome-keyring
BuildRequires:  libgnome-keyring-devel
Requires:       git = %{version}-%{release}
Requires:       gnome-keyring
%description gnome-keyring
%{summary}.
%endif


%prep
# Verify GPG signatures
gpghome="$(mktemp -qd)" # Ensure we don't use any existing gpg keyrings
key="%{SOURCE9}"
src="%{SOURCE0}"
# Ignore noisy output from GnuPG 2.0, used on EL <= 7
# https://bugs.gnupg.org/gnupg/issue1555
gpg2 --dearmor --quiet --batch --yes $key >/dev/null
# Upstream signs the uncompressed tarballs
tar=${src/%.xz/}
xz -dc $src > $tar
gpgv2 --homedir "$gpghome" --quiet --keyring $key.gpg $tar.sign $tar
rm -rf "$tar" "$gpghome" # Cleanup tar files and tmp gpg home dir

%setup -q -n %{name}-%{version}%{?rcrev}
%patch0 -p1
%patch1 -p1
%patch2 -p1

# Remove git-archimport from command list
sed -i '/^git-archimport/d' command-list.txt

# Use these same options for every invocation of 'make'.
# Otherwise it will rebuild in %%install due to flags changes.
cat << \EOF > config.mak
V = 1
CFLAGS = %{optflags}
LDFLAGS = %{__global_ldflags}
NEEDS_CRYPTO_WITH_SSL = 1
USE_LIBPCRE2 = 1
ETC_GITCONFIG = %{_sysconfdir}/gitconfig
DESTDIR = %{buildroot}
INSTALL = install -p
GITWEB_PROJECTROOT = %{_localstatedir}/lib/git
GNU_ROFF = 1
NO_CROSS_DIRECTORY_HARDLINKS = 1
PYTHON_PATH = %{__python2}
htmldir = %{?_pkgdocdir}%{!?_pkgdocdir:%{_docdir}/%{name}-%{version}}
prefix = %{_prefix}
gitwebdir = %{_localstatedir}/www/git
EOF

# Filter bogus perl requires
# packed-refs comes from a comment in contrib/hooks/update-paranoid
%if %{use_new_rpm_filters}
%{?perl_default_filter}
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}perl\\(packed-refs\\)
%if ! %{defined perl_bootstrap}
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}perl\\(Term::ReadKey\\)
%endif
%else
cat << \EOF > %{name}-req
#!/bin/sh
%{__perl_requires} $* |\
sed -e '/perl(packed-refs)/d'
EOF

%global __perl_requires %{_builddir}/%{name}-%{version}/%{name}-req
chmod +x %{__perl_requires}
%endif

%build
make %{?_smp_mflags} all
%if ! 0%{?_without_docs}
make %{?_smp_mflags} doc
%endif

make -C contrib/emacs

%if %{gnome_keyring}
make -C contrib/credential/gnome-keyring/
%endif
%if %{libsecret}
make -C contrib/credential/libsecret/
%endif
make -C contrib/credential/netrc/

make -C contrib/subtree/

# Fix shebang in a few places to silence rpmlint complaints
sed -i -e '1s|#! */usr/bin/env python$|#!%{__python2}|' \
    contrib/fast-import/import-zips.py \
    contrib/hg-to-git/hg-to-git.py \
    contrib/hooks/multimail/git_multimail.py \
    contrib/hooks/multimail/migrate-mailhook-config \
    contrib/hooks/multimail/post-receive.example \
    contrib/svn-fe/svnrdump_sim.py

%install
rm -rf %{buildroot}
make %{?_smp_mflags} INSTALLDIRS=vendor install
%if ! 0%{?_without_docs}
make %{?_smp_mflags} INSTALLDIRS=vendor install-doc
%endif

%global elispdir %{_emacs_sitelispdir}/git
make -C contrib/emacs install \
    emacsdir=%{buildroot}%{elispdir}
for elc in %{buildroot}%{elispdir}/*.elc ; do
    install -pm 644 contrib/emacs/$(basename $elc .elc).el \
    %{buildroot}%{elispdir}
done
install -Dpm 644 %{SOURCE10} \
    %{buildroot}%{_emacs_sitestartdir}/git-init.el

%if %{gnome_keyring}
install -pm 755 contrib/credential/gnome-keyring/git-credential-gnome-keyring \
    %{buildroot}%{gitexecdir}
%endif
%if %{libsecret}
install -pm 755 contrib/credential/libsecret/git-credential-libsecret \
    %{buildroot}%{gitexecdir}
%endif
install -pm 755 contrib/credential/netrc/git-credential-netrc \
    %{buildroot}%{gitexecdir}

make -C contrib/subtree install
make -C contrib/subtree install-doc

mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
install -pm 0644 %{SOURCE12} %{buildroot}%{_sysconfdir}/httpd/conf.d/git.conf
sed "s|@PROJECTROOT@|%{_localstatedir}/lib/git|g" \
    %{SOURCE14} > %{buildroot}%{_sysconfdir}/gitweb.conf

find %{buildroot} -type f -name .packlist -exec rm -f {} ';'
find %{buildroot} -type f -name '*.bs' -empty -exec rm -f {} ';'
find %{buildroot} -type f -name perllocal.pod -exec rm -f {} ';'

# Clean up contrib/subtree to avoid cruft in the git-core-doc docdir
rm -rf contrib/subtree/{INSTALL,Makefile,git-subtree{,.{1,html,sh,txt,xml}},t}

# git-archimport is not supported
find %{buildroot} Documentation -type f -name 'git-archimport*' -exec rm -f {} ';'

exclude_re="archimport|email|git-citool|git-cvs|git-daemon|git-gui|git-remote-bzr|git-remote-hg|gitk|p4|svn"
(find %{buildroot}{%{_bindir},%{_libexecdir}} -type f | grep -vE "$exclude_re" | sed -e s@^%{buildroot}@@) > bin-man-doc-files
(find %{buildroot}{%{_bindir},%{_libexecdir}} -mindepth 1 -type d | grep -vE "$exclude_re" | sed -e 's@^%{buildroot}@%dir @') >> bin-man-doc-files
(find %{buildroot}%{perl_vendorlib} -type f | sed -e s@^%{buildroot}@@) > perl-git-files
(find %{buildroot}%{perl_vendorlib} -mindepth 1 -type d | sed -e 's@^%{buildroot}@%dir @') >> perl-git-files
# Split out Git::SVN files
grep Git/SVN perl-git-files > perl-git-svn-files
sed -i "/Git\/SVN/ d" perl-git-files
%if %{!?_without_docs:1}0
(find %{buildroot}%{_mandir} -type f | grep -vE "$exclude_re|Git" | sed -e s@^%{buildroot}@@ -e 's/$/*/' ) >> bin-man-doc-files
%else
rm -rf %{buildroot}%{_mandir}
%endif

mkdir -p %{buildroot}%{_localstatedir}/lib/git
%if %{use_systemd}
mkdir -p %{buildroot}%{_unitdir}
cp -a %{SOURCE15} %{SOURCE16} %{buildroot}%{_unitdir}
%else
mkdir -p %{buildroot}%{_sysconfdir}/xinetd.d
perl -p \
    -e "s|\@GITEXECDIR\@|%{gitexecdir}|g;" \
    -e "s|\@BASE_PATH\@|%{_localstatedir}/lib/git|g;" \
    %{SOURCE11} > %{buildroot}%{_sysconfdir}/xinetd.d/git
%endif

# Setup bash completion
install -Dpm 644 contrib/completion/git-completion.bash %{buildroot}%{bashcompdir}/git
ln -s git %{buildroot}%{bashcompdir}/gitk

# Install tcsh completion
mkdir -p %{buildroot}%{_datadir}/git-core/contrib/completion
install -pm 644 contrib/completion/git-completion.tcsh \
    %{buildroot}%{_datadir}/git-core/contrib/completion/

# Move contrib/hooks out of %%docdir and make them executable
mkdir -p %{buildroot}%{_datadir}/git-core/contrib
mv contrib/hooks %{buildroot}%{_datadir}/git-core/contrib
chmod +x %{buildroot}%{_datadir}/git-core/contrib/hooks/*
pushd contrib > /dev/null
ln -s ../../../git-core/contrib/hooks
popd > /dev/null

# Install git-prompt.sh
mkdir -p %{buildroot}%{_datadir}/git-core/contrib/completion
install -pm 644 contrib/completion/git-prompt.sh \
    %{buildroot}%{_datadir}/git-core/contrib/completion/

# install git-gui .desktop file
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE13}

# find translations
%find_lang %{name} %{name}.lang
cat %{name}.lang >> bin-man-doc-files

# quiet some rpmlint complaints
chmod -R g-w %{buildroot}
find %{buildroot} -name git-mergetool--lib | xargs chmod a-x
# These files probably are not needed
find . -regex '.*/\.\(git\(attributes\|ignore\)\|perlcriticrc\)' -delete
chmod a-x Documentation/technical/api-index.sh
find contrib -type f | xargs chmod -x

# Split core files
not_core_re="git-(add--interactive|credential-(gnome-keyring|libsecret|netrc)|difftool|filter-branch|instaweb|request-pull|send-mail)|gitweb"
grep -vE "$not_core_re|%{_mandir}" bin-man-doc-files > bin-files-core
grep -vE "$not_core_re" bin-man-doc-files | grep "%{_mandir}" > man-doc-files-core
grep -E  "$not_core_re" bin-man-doc-files \
    | grep -v "credential-gnome-keyring" > bin-man-doc-git-files

##### DOC
# place doc files into %%{_pkgdocdir} and split them into expected packages
# contrib
not_core_doc_re="(git-(cvs|gui|citool|daemon))|p4|svn|email|gitk|gitweb"
mkdir -p %{buildroot}%{_pkgdocdir}/
cp -pr README.md Documentation/*.txt Documentation/RelNotes contrib %{buildroot}%{_pkgdocdir}/
# Remove contrib/credential, it has nothing useful for documentation
rm -rf %{buildroot}%{_pkgdocdir}/contrib/credential/
cp -p gitweb/INSTALL %{buildroot}%{_pkgdocdir}/INSTALL.gitweb
cp -p gitweb/README %{buildroot}%{_pkgdocdir}/README.gitweb

%if ! 0%{?_without_docs}
cp -pr Documentation/*.html Documentation/docbook-xsl.css %{buildroot}%{_pkgdocdir}/
cp -pr Documentation/{howto,technical} %{buildroot}%{_pkgdocdir}/
find %{buildroot}%{_pkgdocdir}/{howto,technical} -type f \
    |grep -o "%{_pkgdocdir}.*$" >> man-doc-files-core
%endif

{
    find %{buildroot}%{_pkgdocdir} -type f -maxdepth 1 \
        | grep -o "%{_pkgdocdir}.*$" \
        | grep -vE "$not_core_doc_re"
    find %{buildroot}%{_pkgdocdir}/{contrib,RelNotes} -type f \
        | grep -o "%{_pkgdocdir}.*$"
    find %{buildroot}%{_pkgdocdir} -type d | grep -o "%{_pkgdocdir}.*$" \
        | sed "s/^/\%dir /"
} >> man-doc-files-core
##### #DOC

%check
%if %{test_links}
find %{buildroot}%{_pkgdocdir} -name "*.html" | xargs linkchecker
%endif

# Tests to skip on all releases and architectures
# t9128-git-svn-cmd-branch - "branch tests" fails randomnly
# t9167-git-svn-cmd-branch-subproject - "branch tests" fails randomnly
GIT_SKIP_TESTS="t9128.3 t9167.3"

%ifarch aarch64 %{arm} %{power64}
# Skip tests which fail on aarch64, arm, and ppc
#
# The following 2 tests use run_with_limited_cmdline, which calls ulimit -s 128
# to limit the maximum stack size.
# t5541.33 'push 2000 tags over http'
# t5551.25 'clone the 2,000 tag repo to check OS command line overflow'
GIT_SKIP_TESTS="$GIT_SKIP_TESTS t5541.33 t5551.25"
%endif

%ifarch s390x
# Skip grep tests which fail intermittently on s390x
## - probably it is because of current troubles with binutils on s390x. Will
##   try tests when troubles on s390x will be resolved
GIT_SKIP_TESTS="$GIT_SKIP_TESTS t7008 t7810 t7811 t7812 t7813 t7814"
%endif

export GIT_SKIP_TESTS

# Set LANG so various UTF-8 tests are run
export LANG=en_US.UTF-8

# Set SVNSERVE_PORT to run svnserve tests
export SVNSERVE_PORT=9000

# Run the tests
make %{?make_test_opts} test

%clean
rm -rf %{buildroot}

%if %{use_systemd}
%post daemon
%systemd_post git@.service

%preun daemon
%systemd_preun git@.service

%postun daemon
%systemd_postun_with_restart git@.service
%endif

%files -f bin-man-doc-git-files
%defattr(-,root,root)
%if 0%{?fedora} || 0%{?rhel} >= 7
%{elispdir}
%{_emacs_sitestartdir}/git-init.el
%endif
%{_datadir}/git-core/contrib/hooks/update-paranoid
%{_datadir}/git-core/contrib/hooks/setgitperms.perl
%{_datadir}/git-core/templates/hooks/pre-rebase.sample
%{_datadir}/git-core/templates/hooks/prepare-commit-msg.sample

%files core -f bin-files-core
%defattr(-,root,root)
#NOTE: this is only use of the %%doc macro in this spec file and should not
#      be used elsewhere
%{!?_licensedir:%global license %doc}
%license COPYING
# exclude is best way here because of troubles with symlinks inside git-core/
%exclude %{_datadir}/git-core/contrib/hooks/update-paranoid
%exclude %{_datadir}/git-core/contrib/hooks/setgitperms.perl
%exclude %{_datadir}/git-core/templates/hooks/pre-rebase.sample
%exclude %{_datadir}/git-core/templates/hooks/prepare-commit-msg.sample
%{bashcomproot}
%{_datadir}/git-core/

%files core-doc -f man-doc-files-core
%defattr(-,root,root)
%exclude %{_pkgdocdir}/contrib/*/*.py[co]
%{_pkgdocdir}/contrib/hooks

%files p4
%defattr(-,root,root)
%{gitexecdir}/*p4*
%{gitexecdir}/mergetools/p4merge
%{_pkgdocdir}/*p4*.txt
%{!?_without_docs: %{_mandir}/man1/*p4*.1*}
%{!?_without_docs: %{_pkgdocdir}/*p4*.html }

%files svn
%defattr(-,root,root)
%{gitexecdir}/*svn*
#NOTE: what about svn-fe
%{_pkgdocdir}/*svn*.txt
%{!?_without_docs: %{_mandir}/man1/*svn*.1*}
%{!?_without_docs: %{_pkgdocdir}/*svn*.html }

%files cvs
%defattr(-,root,root)
%{_pkgdocdir}/*git-cvs*.txt
%{_bindir}/git-cvsserver
%{gitexecdir}/*cvs*
%{!?_without_docs: %{_mandir}/man1/*cvs*.1*}
%{!?_without_docs: %{_pkgdocdir}/*git-cvs*.html }

%files email
%defattr(-,root,root)
%{_pkgdocdir}/*email*.txt
%{gitexecdir}/*email*
%{!?_without_docs: %{_mandir}/man1/*email*.1*}
%{!?_without_docs: %{_pkgdocdir}/*email*.html }

%files gui
%defattr(-,root,root)
%{gitexecdir}/git-gui*
%{gitexecdir}/git-citool
%{_datadir}/applications/*git-gui.desktop
%{_datadir}/git-gui/
%{_pkgdocdir}/git-gui.txt
%{_pkgdocdir}/git-citool.txt
%{!?_without_docs: %{_mandir}/man1/git-gui.1*}
%{!?_without_docs: %{_pkgdocdir}/git-gui.html}
%{!?_without_docs: %{_mandir}/man1/git-citool.1*}
%{!?_without_docs: %{_pkgdocdir}/git-citool.html}

%files -n gitk
%defattr(-,root,root)
%{_pkgdocdir}/*gitk*.txt
%{_bindir}/*gitk*
%{_datadir}/gitk
%{!?_without_docs: %{_mandir}/man1/*gitk*.1*}
%{!?_without_docs: %{_pkgdocdir}/*gitk*.html }

%files -n perl-Git -f perl-git-files
%defattr(-,root,root)
%exclude %{_mandir}/man3/*Git*SVN*.3pm*
%{!?_without_docs: %{_mandir}/man3/*Git*.3pm*}

%files -n perl-Git-SVN -f perl-git-svn-files
%defattr(-,root,root)
%{!?_without_docs: %{_mandir}/man3/*Git*SVN*.3pm*}

%if 0%{?rhel} && 0%{?rhel} <= 6
%files -n emacs-git
%defattr(-,root,root)
%{_pkgdocdir}/contrib/emacs/README
%dir %{elispdir}
%{elispdir}/*.elc
%{_emacs_sitestartdir}/git-init.el

%files -n emacs-git-el
%defattr(-,root,root)
%{elispdir}/*.el
%endif

%files daemon
%defattr(-,root,root)
%{_pkgdocdir}/git-daemon*.txt
%if %{use_systemd}
%{_unitdir}/git.socket
%{_unitdir}/git@.service
%else
%config(noreplace)%{_sysconfdir}/xinetd.d/git
%endif
%{gitexecdir}/git-daemon
%{_localstatedir}/lib/git
%{!?_without_docs: %{_mandir}/man1/git-daemon*.1*}
%{!?_without_docs: %{_pkgdocdir}/git-daemon*.html}

%files -n gitweb
%defattr(-,root,root)
%{_pkgdocdir}/*.gitweb
%{_pkgdocdir}/gitweb*.txt
%{!?_without_docs: %{_pkgdocdir}/gitweb*.html}
%config(noreplace)%{_sysconfdir}/gitweb.conf
%config(noreplace)%{_sysconfdir}/httpd/conf.d/git.conf
%{_localstatedir}/www/git/

%if %{gnome_keyring}
%files gnome-keyring
%defattr(-,root,root)
%{gitexecdir}/git-credential-gnome-keyring
%endif


%files all
# No files for you!

%changelog
* Wed Nov 29 2017 Todd Zullinger <tmz@pobox.com> - 2.15.1-2
- Fix debuginfo for gnome-keyring and libsecret credential helpers

* Tue Nov 28 2017 Todd Zullinger <tmz@pobox.com> - 2.15.1-1
- Update to 2.15.1

* Tue Nov 21 2017 Todd Zullinger <tmz@pobox.com>
- Add tcl/tk BuildRequires
- Enable support for release candidate builds

* Tue Nov 07 2017 Todd Zullinger <tmz@pobox.com> - 2.15.0-2
- Fix git-clone memory exhaustion (CVE-2017-15298)
  Resolves: #1510455, #1510457
- Disable cross-directory hardlinks
- Drop ancient obsoletes for git and git-arch
- Update summary/description of numerous subpackages
- Fix shebang in a few places to silence rpmlint complaints
- Fix t9020-remote-svn failure when setting PYTHON_PATH
- Rename %%gitcoredir to %%gitexecdir; upstream uses the latter
- Move commands which no longer require perl into git-core
- Move filter-branch out of core, it needs perl now
- Improve test suite coverage

* Mon Oct 30 2017 Todd Zullinger <tmz@pobox.com> - 2.15.0-1
- Update to 2.15.0

* Mon Oct 23 2017 Todd Zullinger <tmz@pobox.com> - 2.14.3-1
- Update to 2.14.3

* Tue Sep 26 2017 Todd Zullinger <tmz@pobox.com> - 2.14.2-2
- Update to 2.14.2

* Thu Aug 10 2017 Todd Zullinger <tmz@pobox.com> - 2.14.1-2
- Rebuild for rpm-4.14 bug (#1480407)

* Thu Aug 10 2017 Todd Zullinger <tmz@pobox.com> - 2.14.1-1
- Update to 2.14.1 (resolves CVE-2017-1000117)

* Tue Aug 08 2017 Iryna Shcherbina <ishcherb@redhat.com> - 2.14.0-2
- Add a build-time dependency on python2-devel for p4
  Resolves: #1479713
- Skip all grep tests on s390x for now because it failes intermittently

* Fri Aug 04 2017 Todd Zullinger <tmz@pobox.com> - 2.14.0-1
- Update to 2.14.0
- Use pcre2 library
- git-p4: explicitly require python2

* Tue Aug 01 2017 Todd Zullinger <tmz@pobox.com> - 2.13.4-1
- Update to 2.13.4
- Remove EL-5 and old Fedora conditionals

* Sun Jul 30 2017 Florian Weimer <fweimer@redhat.com> - 2.13.3-3
- Rebuild with binutils fix for ppc64le (#1475636)

* Thu Jul 20 2017 Petr Stodulka <pstodulk@redhat.com> - 2.13.3-2
- Move documentation files from all subpackages into the %%{_pkgdocdir}
  directory, so links inside doc and man files are correct
  Resolves: #1357438
- Quiet a few rpmlint complaints regarding hidden files in contrib dir
- Remove explicit libcurl requirement from git-core

* Thu Jul 13 2017 Gwyn Ciesla <limburgher@gmail.com> - 2.13.3-1
- Update to 2.13.3

* Sun Jun 25 2017 Todd Zullinger <tmz@pobox.com> - 2.13.2-1
- Update to 2.13.2
- Skip grep tests which fail intermittently on s390x

* Wed Jun 07 2017 Jitka Plesnikova <jplesnik@redhat.com> - 2.13.1-2
- Perl 5.26 re-rebuild of bootstrapped packages

* Mon Jun 05 2017 Todd Zullinger <tmz@pobox.com> - 2.13.1-1
- Update to 2.13.1

* Sun Jun 04 2017 Jitka Plesnikova <jplesnik@redhat.com> - 2.13.0-3
- Perl 5.26 rebuild

* Wed May 17 2017 Todd Zullinger <tmz@pobox.com> - 2.13.0-2
- Use default, collision-detecting SHA1 implementation

* Tue May 09 2017 Todd Zullinger <tmz@pobox.com> - 2.13.0-1
- Update to 2.13.0 (resolves CVE-2017-8386)

* Wed Mar 29 2017 Gwyn Ciesla <limburgher@gmail.com> - 2.12.2-1
- Update to 2.12.2

* Tue Mar 21 2017 Gwyn Ciesla <limburgher@gmail.com> - 2.12.1-1
- Update to 2.12.1

* Mon Feb 27 2017 Jon Ciesla <limburgher@gmail.com> - 2.12.0-1
- Update to 2.12.0

* Fri Feb 17 2017 Petr Stodulka <pstodulk@redhat.com> - 2.11.1-3
- remove non-ASCII characters from description and title of packages
- fix requiremets
- fix spec to be compatible for other systems
- remove deprecated credential-gnome-keyring

* Fri Feb 17 2017 Todd Zullinger <tmz@pobox.com> - 2.11.1-3
- Remove unnecessary rsync requirement from git-core
- Move gnome-keyring credential helper from git-core to git
- Enable libsecret credential helper
- Run git test suite
- Use %%{_mandir} in git/git-core file list filters
- Fix version of emacs-git and emacs-git-el provides
- Clean up contrib/{credential,subtree} to avoid cruft in git-core-doc
- Fix a number of macro-in-comment warnings from rpmlint

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.11.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Feb 03 2017 Jon Ciesla <limburgher@gmail.com> - 2.11.1-1
- Update to 2.11.1

* Wed Nov 30 2016 Jon Ciesla <limburgher@gmail.com> - 2.11.0-1
- Update to 2.11.0

* Mon Oct 31 2016 Jon Ciesla <limburgher@gmail.com> - 2.10.2-1
- Update to 2.10.2

* Tue Oct 04 2016 Jon Ciesla <limburgher@gmail.com> - 2.10.1-1
- Update to 2.10.1

* Sat Sep 03 2016 Todd Zullinger <tmz@pobox.com> - 2.10.0-1
- Update to 2.10.0

* Mon Aug 15 2016 Jon Ciesla <limburgher@gmail.com> - 2.9.3-1
- Update to 2.9.3.

* Fri Jul 15 2016 Jon Ciesla <limburgher@gmail.com> - 2.9.2-1
- Update to 2.9.2.

* Tue Jul 12 2016 Jon Ciesla <limburgher@gmail.com> - 2.9.1-1
- Update to 2.9.1.

* Tue Jun 14 2016 Jon Ciesla <limburgher@gmail.com> - 2.9.0-1
- Update to 2.9.0.

* Wed Jun 08 2016 Jon Ciesla <limburgher@gmail.com> - 2.8.4-1
- Update to 2.8.4.

* Fri May 20 2016 Jitka Plesnikova <jplesnik@redhat.com> - 2.8.3-2
- Perl 5.24 rebuild

* Thu May 19 2016 Todd Zullinger <tmz@pobox.com> - 2.8.3-1
- Update to 2.8.3

* Thu May 19 2016 Jitka Plesnikova <jplesnik@redhat.com> - 2.8.2-5
- Perl 5.24 re-rebuild of bootstrapped packages

* Wed May 18 2016 Todd Zullinger <tmz@pobox.com> - 2.8.2-4
- Use perl(MOD::NAME) format for perl-DBD-SQLite and perl-Digest-MD5 deps
- Define __global_ldflags on EL < 7 (#1337137)

* Wed May 18 2016 Jitka Plesnikova <jplesnik@redhat.com> - 2.8.2-3
- Perl 5.24 re-rebuild of bootstrapped packages

* Sun May 15 2016 Jitka Plesnikova <jplesnik@redhat.com> - 2.8.2-2
- Perl 5.24 rebuild

* Fri Apr 29 2016 Todd Zullinger <tmz@pobox.com> - 2.8.2-1
- Update to 2.8.2

* Mon Apr 11 2016 Todd Zullinger <tmz@pobox.com> - 2.8.1-3
- Set LDFLAGS for hardened builds (#1289728)

* Wed Apr 06 2016 Paolo Bonzini <pbonzini@redhat.com> - 2.8.1-2
- Install git-credentials-netrc (#1303358)

* Tue Apr 05 2016 Jon Ciesla <limburgher@gmail.com> - 2.8.1-1
- Update to 2.8.1.

* Tue Mar 29 2016 Neal Gompa <ngompa13{%}gmail{*}com> - 2.8.0-1
- Update to 2.8.0
- Use license macro for COPYING

* Sun Mar 27 2016 Todd Zullinger <tmz@pobox.com> - 2.7.4-2
- Use https for URL / Source and smaller tar.xz files
- Check upstream GPG signatures in %%prep

* Tue Mar 22 2016 Konrad Scherer <Konrad.Scherer@windriver.com>
- Workaround missing git subtree documentation in prebuilt docs (bug 1320210)
- Only add git-cvsserver binary once if the core dir matches the bin dir as it
  does on el5 (bug 1320210)

* Tue Mar 22 2016 Todd Zullinger <tmz@pobox.com>
- Conditionalize bash-completion pkg-config usage for EL <= 6 (bug 1320210)

* Fri Mar 18 2016 David Woodhouse <dwmw2@infradead.org> - 2.7.4-1
- Update to 2.7.4 (for CVE-2016-2315, CVE-2016-2324)
  Resolves: #1318220

* Mon Mar 14 2016 Jon Ciesla <limburgher@gmail.com> - 2.7.3-1
- Update to 2.7.3.

* Tue Feb 23 2016 Jon Ciesla <limburgher@gmail.com> - 2.7.2-1
- Update to 2.7.2.

* Sat Feb 06 2016 Jon Ciesla <limburgher@gmail.com> - 2.7.1-1
- Update to 2.7.1.

* Thu Feb 04 2016 Petr Stodulka <pstodulk@redhat.com> - 2.7.0-3
- remove all '.gitignore' files from packages

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jan 05 2016 Jon Ciesla <limburgher@gmail.com> - 2.7.0-1
- Update to 2.7.0.
- Infinite loop patch appears obsolete.

* Wed Dec 09 2015 Jon Ciesla <limburgher@gmail.com> - 2.6.4-1
- Update to 2.6.4.

* Fri Nov 27 2015 Petr Stodulka <pstodulk@redhat.com> - 2.6.3-2
- found 2 perl scripts in git-core, move them to git package
  (#1284688)

* Fri Nov 06 2015 Jon Ciesla <limburgher@gmail.com> - 2.6.3-1
- Update to 2.6.3.

* Tue Nov 03 2015 Petr Stodulka <pstodulk@gmail.com> - 2.6.2-2
- provides failback for the macro _pkgdocdir (#1277550)

* Sat Oct 17 2015 Jon Ciesla <limburgher@gmail.com> - 2.6.2-1
- Update to 2.6.2.

* Tue Oct 06 2015 Jon Ciesla <limburgher@gmail.com> - 2.6.1-1
- Update to 2.6.1.

* Tue Sep 29 2015 Jon Ciesla <limburgher@gmail.com> - 2.6.0-1
- Update to 2.6.0.

* Fri Sep 18 2015 Jon Ciesla <limburgher@gmail.com> - 2.5.3-1
- Update to 2.5.3.

* Fri Sep 11 2015 Jon Ciesla <limburgher@gmail.com> - 2.5.2-1
- Update to 2.5.2.

* Sat Aug 29 2015 Petr Stodulka <pstodulk@redhat.com> - 2.5.1-1
- Update to 2.5.1

* Tue Jul 28 2015 Jon Ciesla <limburgher@gmail.com> - 2.5.0-1
- Update to 2.5.0.

* Thu Jul 16 2015 Petr Stodulka <pstodulk@redhat.com> - 2.4.6-1
- New upstream release 2.4.6

* Tue Jul  7 2015 Jonathan Underwood <jonathan.underwood@gmail.com> - 2.4.5-2
- Comply with modern Emacs packaging guidelines on recent Fedora
  No longer split out emacs-git and emacs-git-el sub-packages on recent Fedora
  Require emacs-filesystem on recent Fedora (#1234552)

* Fri Jun 26 2015 Jon Ciesla <limburgher@gmail.com> - 2.4.5-1
- Update to 2.4.5.

* Mon Jun 22 2015  Petr Stodulka <pstodulk@gmail.com> - 2.4.4-2
- git-svn - added requires for perl-Digest-MD5 (#1218176)
- solve troubles with infinite loop due to broken symlink (probably
  shouldn't be problem here, but it's reproducible manually)
  (#1204193)

* Tue Jun 16 2015 Jon Ciesla <limburgher@gmail.com> - 2.4.4-1
- Update to 2.4.4.

* Wed Jun 10 2015 Jitka Plesnikova <jplesnik@redhat.com> - 2.4.3-4
- Perl 5.22 re-rebuild of bootstrapped packages

* Tue Jun 09 2015 Jitka Plesnikova <jplesnik@redhat.com> - 2.4.3-3
- Perl 5.22 rebuild

* Mon Jun 08 2015 Petr Stodulka <pstodulk@redhat.com> - 2.4.3-2
- separate documentation files from git-core package to git-core-doc
  including core man pages

* Sat Jun 06 2015 Jon Ciesla <limburgher@gmail.com> - 2.4.3-1
- Update to 2.4.3.

* Fri Jun 05 2015 Jitka Plesnikova <jplesnik@redhat.com>
- Perl 5.22 rebuild

* Wed Jun 03 2015 Petr Stodulka <pstodulk@redhat.com> - 2.4.2-2
- split create subpackage git-core (perl-less) from git package
- git package requires git-core and it has same tool set as
  before
- relevant docs are part of git-core package too
- removed proved and obsoletes in git for git-core

* Tue May 26 2015 Jon Ciesla <limburgher@gmail.com> - 2.4.2-1
- Update to 2.4.2.

* Thu May 14 2015 Jon Ciesla <limburgher@gmail.com> - 2.4.1-1
- Update to 2.4.1.

* Fri May 01 2015 Jon Ciesla <limburgher@gmail.com> - 2.4.0-1
- Update to 2.4.0.

* Tue Apr 28 2015 Jon Ciesla <limburgher@gmail.com> - 2.3.7-1
- Update to 2.3.7.

* Wed Apr 22 2015 Jon Ciesla <limburgher@gmail.com> - 2.3.6-1
- Update to 2.3.6.

* Mon Apr 06 2015 Jon Ciesla <limburgher@gmail.com> - 2.3.5-1
- Update to 2.3.5.

* Tue Mar 24 2015 Petr Stodulka <pstodulk@redhat.com> - 2.3.4-1
- Update to 2.3.4.

* Mon Mar 16 2015 Jon Ciesla <limburgher@gmail.com> - 2.3.3-1
- Update to 2.3.3.

* Mon Mar 09 2015 Jon Ciesla <limburgher@gmail.com> - 2.3.2-1
- Update to 2.3.2.

* Fri Feb 27 2015 Jon Ciesla <limburgher@gmail.com> - 2.3.1-1
- Update to 2.3.1.

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 2.3.0-2
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Fri Feb 06 2015 Jon Ciesla <limburgher@gmail.com> - 2.3.0-1
- Update to 2.3.0.

* Tue Jan 27 2015 Ville Skyttä <ville.skytta@iki.fi> - 2.2.2-2
- Install bash completion to %%{_datadir}/bash-completion/completions

* Fri Jan 23 2015 Jon Ciesla <limburgher@gmail.com> - 2.2.2-1
- Update to 2.2.2.

* Thu Jan 08 2015 Jon Ciesla <limburgher@gmail.com> - 2.2.1-1
- Update to 2.2.1.

* Thu Dec 11 2014 Petr Stodulka <pstodulk@redhat.com> - 2.2.0-3
- removed subpackage git-hg which is replaced by git-remote-hg from
  separated package

* Fri Nov 28 2014 Petr Stodulka <pstodulk@redhat.com> - 2.2.0-2
- removed subpackage git-bzr which is replaced by git-remote-bzr from
  separated package

* Fri Nov 28 2014 Petr Stodulka <pstodulk@redhat.com> - 2.2.0-1
- 2.2.0

* Fri Oct 24 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.1.0-5
- Rename the git.service into git@.service fixing
  https://bugzilla.redhat.com/980574

* Mon Sep 08 2014 Jitka Plesnikova <jplesnik@redhat.com> - 2.1.0-4
- Perl 5.20 re-rebuild of bootstrapped packages

* Thu Aug 28 2014 Jitka Plesnikova <jplesnik@redhat.com> - 2.1.0-3
- Perl 5.20 rebuild

* Tue Aug 26 2014 Jitka Plesnikova <jplesnik@redhat.com> - 2.1.0-2
- Disable requires perl(Term::ReadKey) when perl bootstraping

* Mon Aug 18 2014 Ondrej Oprala <ooprala@redhat.com - 2.1.0-1
- 2.1.0

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jul 31 2014 Ondrej Oprala <ooprala@redhat.com - 2.0.4-1
- 2.0.4

* Mon Jul 28 2014 Ondrej Oprala <ooprala@redhat.com - 2.0.3-1
- 2.0.3

* Fri Jul 11 2014 Ondrej Oprala <ooprala@redhat.com - 2.0.1-1
- 2.0.1

* Tue Jun 10 2014 Ondrej Oprala <ooprala@redhat.com> - 2.0.0-4
- Change source URLs, as googlecode doesn't have up-to-date tarballs

* Tue Jun 10 2014 Ondrej Oprala <ooprala@redhat.com> - 2.0.0-3
- Conditionalize an ancient obsolete

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 29 2014 Ondrej Oprala <ooprala@redhat.com> - 2.0.0-1
- Update to 2.0.0

* Mon May 19 2014 Jon Ciesla <limburgher@gmail.com> - 1.9.3-1
- Update to 1.9.3

* Mon Feb 17 2014 Ondrej Oprala <ooprala@redhat.com> - 1.9.0-1
- Update to 1.9.0

* Thu Jan 16 2014 Todd Zullinger <tmz@pobox.com> - 1.8.5.3-2
- Drop unused python DESTIR patch
- Consolidate settings for Fedora 19+ and EL 7+
- Use new rpm filtering on Fedora 19+ and EL 7+
- Rebuild with file-5.14-14 (#1026760)

* Thu Jan 16 2014 Ondrej Oprala <ooprala@redhat.com> - 1.8.5.3-1
* Update to 1.8.5.3

* Wed Dec 18 2013 Ondrej Oprala <ooprala@redhat.com> - 1.8.5.2-1
* Update to 1.8.5.2

* Wed Nov 13 2013 Ville Skyttä <ville.skytta@iki.fi> - 1.8.4.2-2
- Fix htmldir when doc dir is unversioned (#993779).

* Tue Oct 29 2013 Todd Zullinger <tmz@pobox.com> - 1.8.4.2-1
- Update to 1.8.4.2 (#1024497)

* Sat Oct 05 2013 Todd Zullinger <tmz@pobox.com>
- Add mercurial version requirement to git-hg, for those rebuilding on EL

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jul 15 2013 Petr Pisar <ppisar@redhat.com> - 1.8.3.1-2
- Perl 5.18 rebuild

* Fri Jun 14 2013 Todd Zullinger <tmz@pobox.com> - 1.8.3.1-1
- Update to 1.8.3.1
- Add bzr and hg subpackages, thanks to Michael Scherer (#974800)

* Mon May 13 2013 Jon Ciesla <limburgher@gmail.com> - 1.8.2.1-4
- Fix typo introduced in 1.8.2-3, fixed desktop tag.

* Wed May  1 2013 Tom Callaway <spot@fedoraproject.org> - 1.8.2.1-3
- conditionalize systemd vs xinetd
- cleanup systemd handling (it was not quite right in -2)

* Tue Apr 30 2013 Tom Callaway <spot@fedoraproject.org> - 1.8.2.1-2
- switch to systemd instead of xinetd (bz 737183)

* Sun Apr 14 2013 Todd Zullinger <tmz@pobox.com> - 1.8.2.1-1
- Update to 1.8.2.1
- Exclude optional perl(YAML::Any) dependency on EL-5

* Wed Apr 10 2013 Jon Ciesla <limburgher@gmail.com> - 1.8.2-3
- Drop desktop vendor tag for >= f19.

* Wed Mar 27 2013 Todd Zullinger <tmz@pobox.com> - 1.8.2-2
- Require perl(Term::ReadKey) for git add --interactive (#928328)
- Drop DESTDIR from python instlibdir
- Fix bogus changelog dates

* Tue Mar 19 2013 Adam Tkac <atkac redhat com> - 1.8.2-1
- update to 1.8.2
- 0001-DESTDIR-support-in-contrib-subtree-Makefile.patch has been merged

* Tue Feb 26 2013 Todd Zullinger <tmz@pobox.com> - 1.8.1.4-2
- Update asciidoc requirements, drop unsupported ASCIIDOC7
- Define GNU_ROFF to force ASCII apostrophes in manpages (so copy/paste works)
- Install tcsh completion (requires manual setup by users)
- Clean up dist conditionals, don't pretend to support EL-4 builds
- Use prebuilt documentation on EL-5, where asciidoc is too old
- Respect gitexecdir variable in git-subtree install

* Wed Feb 20 2013 Adam Tkac <atkac redhat com> - 1.8.1.4-1
- update to 1.8.1.4

* Wed Jan 30 2013 Adam Tkac <atkac redhat com> - 1.8.1.2-1
- update to 1.8.1.2
- own directories which should be owned (#902517)

* Thu Jan 03 2013 Adam Tkac <atkac redhat com> - 1.8.1-1
- update to 1.8.1
- build git-svn as arch subpkg due to new git-remote-testsvn binary

* Tue Dec 11 2012 Adam Tkac <atkac redhat com> - 1.8.0.2-1
- update to 1.8.0.2

* Thu Dec 06 2012 Adam Tkac <atkac redhat com> - 1.8.0.1-2
- don't install some unneeded credential-gnome-keyring stuff

* Thu Nov 29 2012 Adam Tkac <atkac redhat com> - 1.8.0.1-1
- update to 1.8.0.1
- include git-subtree in git rpm (#864651)

* Mon Oct 29 2012 Adam Tkac <atkac redhat com> - 1.8.0-1
- update to 1.8.0
- include git-credential-gnome-keyring helper in git pkg
- 0001-cvsimport-strip-all-inappropriate-tag-strings.patch was merged

* Thu Oct 25 2012 Adam Tkac <atkac redhat com> - 1.7.12.1-2
- move git-prompt.sh into usr/share/git-core/contrib/completion (#854061)

* Thu Sep 27 2012 Adam Tkac <atkac redhat com> - 1.7.12.1-1
- update to 1.7.12.1
- cvsimport should skip more characters (#850640)

* Thu Aug 23 2012 Todd Zullinger <tmz@pobox.com> - 1.7.12-2
- Install git-prompt.sh which provides __git_ps1()

* Wed Aug 22 2012 Adam Tkac <atkac redhat com> - 1.7.12-1
- update to 1.7.12

* Wed Aug 15 2012 Todd Zullinger <tmz@pobox.com> - 1.7.11.5-1
- Update to 1.7.11.5
- Add git-p4 subpackage (#844008)

* Tue Aug 07 2012 Adam Tkac <atkac redhat com> - 1.7.11.4-1
- update to 1.7.11.4

* Fri Jul 27 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.11.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul 25 2012 Todd Zullinger <tmz@pobox.com> - 1.7.11.2-2
- Split perl(Git::SVN) into its own package (#843182)

* Mon Jul 16 2012 Adam Tkac <atkac redhat com> - 1.7.11.2-1
- update to 1.7.11.2

* Thu Jun 28 2012 Petr Pisar <ppisar@redhat.com> - 1.7.10.4-2
- Perl 5.16 rebuild

* Fri Jun 15 2012 Adam Tkac <atkac redhat com> - 1.7.10.4-1
- update to 1.7.10.4

* Thu Jun 07 2012 Petr Pisar <ppisar@redhat.com> - 1.7.10.2-2
- Perl 5.16 rebuild

* Mon May 14 2012 Adam Tkac <atkac redhat com> - 1.7.10.2-1
- update to 1.7.10.2

* Thu May 03 2012 Adam Tkac <atkac redhat com> - 1.7.10.1-1
- update to 1.7.10.1

* Tue Apr 10 2012 Adam Tkac <atkac redhat com> - 1.7.10-1
- update to 1.7.10

* Fri Mar 30 2012 Adam Tkac <atkac redhat com> - 1.7.9.5-1
- update to 1.7.9.5

* Thu Mar 08 2012 Adam Tkac <atkac redhat com> - 1.7.9.3-1
- update to 1.7.9.3

* Wed Feb 15 2012 Todd Zullinger <tmz@pobox.com> - 1.7.9.1-1
- Update to 1.7.9.1
- Fix EPEL builds (rpm doesn't accept multiple -f options in %%files)

* Fri Feb 10 2012 Petr Pisar <ppisar@redhat.com> - 1.7.9-2
- Rebuild against PCRE 8.30

* Mon Jan 30 2012 Adam Tkac <atkac redhat com> - 1.7.9-1
- update to 1.7.9

* Thu Jan 19 2012 Adam Tkac <atkac redhat com> - 1.7.8.4-1
- update to 1.7.8.4

* Thu Jan 12 2012 Adam Tkac <atkac redhat com> - 1.7.8.3-1
- update to 1.7.8.3

* Mon Jan 02 2012 Adam Tkac <atkac redhat com> - 1.7.8.2-1
- update to 1.7.8.2

* Fri Dec 23 2011 Adam Tkac <atkac redhat com> - 1.7.8.1-1
- update to 1.7.8.1

* Wed Dec 07 2011 Adam Tkac <atkac redhat com> - 1.7.8-1
- update to 1.7.8

* Tue Nov 29 2011 Adam Tkac <atkac redhat com> - 1.7.7.4-1
- update to 1.7.7.4

* Thu Nov 10 2011 Adam Tkac <atkac redhat com> - 1.7.7.3-1
- update to 1.7.7.3

* Mon Nov 07 2011 Adam Tkac <atkac redhat com> - 1.7.7.2-1
- update to 1.7.7.2

* Tue Nov 01 2011 Adam Tkac <atkac redhat com> - 1.7.7.1-1
- update to 1.7.7.1

* Wed Oct 26 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.7-2
- Rebuilt for glibc bug#747377

* Thu Oct 20 2011 Adam Tkac <atkac redhat com> - 1.7.7-1
- update to 1.7.7
  - git-1.6-update-contrib-hooks-path.patch is no longer needed

* Mon Sep 26 2011 Adam Tkac <atkac redhat com> - 1.7.6.4-1
- update to 1.7.6.4

* Wed Sep 07 2011 Todd Zullinger <tmz@pobox.com> - 1.7.6.2-1
- Update to 1.7.6.2
- Fixes incompatibility caused by git push --quiet fix
  http://thread.gmane.org/gmane.comp.version-control.git/180652

* Mon Aug 29 2011 Todd Zullinger <tmz@pobox.com> - 1.7.6.1-2
- Build with PCRE support (#734269)

* Fri Aug 26 2011 Todd Zullinger <tmz@pobox.com> - 1.7.6.1-1
- Update to 1.7.6.1
- Include gpg signature for tarball in SRPM

* Fri Aug 05 2011 Todd Zullinger <tmz@pobox.com> - 1.7.6-5
- Fix git push --quiet, thanks to Clemens Buchacher (#725593)
- Obsolete git-arch as needed

* Tue Jul 26 2011 Todd Zullinger <tmz@pobox.com> - 1.7.6-4
- Drop git-arch on fedora >= 16, the tla package has been retired
- Rework most spec file dist conditionals to make future changes easier

* Thu Jul 21 2011 Petr Sabata <contyk@redhat.com> - 1.7.6-3
- Perl mass rebuild

* Wed Jul 20 2011 Petr Sabata <contyk@redhat.com> - 1.7.6-2
- Perl mass rebuild

* Wed Jun 29 2011 Adam Tkac <atkac redhat com> - 1.7.6-1
- update to 1.7.6

* Mon Jun 20 2011 Marcela Mašláňová <mmaslano@redhat.com> - 1.7.5.4-2
- Perl mass rebuild

* Thu Jun 09 2011 Adam Tkac <atkac redhat com> - 1.7.5.4-1
- update to 1.7.5.4

* Tue May 24 2011 Adam Tkac <atkac redhat com> - 1.7.5.2-1
- update to 1.7.5.2

* Thu May 05 2011 Adam Tkac <atkac redhat com> - 1.7.5.1-1
- update to 1.7.5.1

* Wed Apr 27 2011 Adam Tkac <atkac redhat com> - 1.7.5-1
- update to 1.7.5

* Mon Apr 11 2011 Adam Tkac <atkac redhat com> - 1.7.4.4-1
- update to 1.7.4.4

* Mon Mar 28 2011 Adam Tkac <atkac redhat com> - 1.7.4.2-1
- update to 1.7.4.2
- move man3/Git.3pm file to perl-Git subpkg (#664889)
- add perl-DBD-SQLite dependency to git-cvs (#602410)

* Sun Feb 13 2011 Todd Zullinger <tmz@pobox.com> - 1.7.4.1-1
- Update to 1.7.4.1
- Clean up documentation settings (the defaults changed in 1.7.4)
- Improve EL-5 compatibility, thanks to Kevin Fenzi for emacs testing

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 31 2011 Adam Tkac <atkac redhat com> - 1.7.4-1
- update to 1.7.4

* Wed Jan 19 2011 Adam Tkac <atkac redhat com> - 1.7.3.5-1
- update to 1.7.3.5

* Thu Dec 16 2010 Adam Tkac <atkac redhat com> - 1.7.3.4-1
- update to 1.7.3.4

* Mon Dec 06 2010 Adam Tkac <atkac redhat com> - 1.7.3.3-1
- update to 1.7.3.3

* Fri Oct 22 2010 Adam Tkac <atkac redhat com> - 1.7.3.2-1
- update to 1.7.3.2

* Thu Sep 30 2010 Adam Tkac <atkac redhat com> - 1.7.3.1-1
- update to 1.7.3.1

* Wed Sep 29 2010 jkeating - 1.7.3-3
- Rebuilt for gcc bug 634757

* Mon Sep 20 2010 Todd Zullinger <tmz@pobox.com> - 1.7.3-2
- Ensure the release notes are included in %%doc

* Sun Sep 19 2010 Todd Zullinger <tmz@pobox.com> - 1.7.3-1
- Update to 1.7.3

* Tue Sep 07 2010 Adam Tkac <atkac redhat com> - 1.7.2.3-1
- update to 1.7.2.3

* Fri Aug 20 2010 Adam Tkac <atkac redhat com> - 1.7.2.2-1
- update to 1.7.2.2

* Fri Jul 30 2010 Thomas Spura <tomspur@fedoraproject.org> - 1.7.2.1-2
- cherry-pick: "Do not unquote + into ' ' in URLs"

* Thu Jul 29 2010 Todd Zullinger <tmz@pobox.com> - 1.7.2.1-1
- Update to git-1.7.2.1

* Thu Jul 22 2010 Adam Tkac <atkac redhat com> - 1.7.2-1
- update to 1.7.2

* Fri Jul 02 2010 Adam Tkac <atkac redhat com> - 1.7.1.1-1
- update to 1.7.1.1

* Fri Jun 25 2010 Adam Tkac <atkac redhat com> - 1.7.1-2
- rebuild against new perl

* Tue May 04 2010 Todd Zullinger <tmz@pobox.com> - 1.7.1-1
- git-1.7.1
- Fix conditionals for EL-6
- Comply with Emacs add-on packaging guidelines (#573423), Jonathan Underwood
  - Place elisp source files in separate emacs-git-el package
  - Place git support files in own directory under site-lisp
  - Use Emacs packaging macros

* Thu Apr 29 2010 Marcela Maslanova <mmaslano@redhat.com> - 1.7.0.1-2
- Mass rebuild with perl-5.12.0

* Mon Mar 01 2010 Todd Zullinger <tmz@pobox.com> - 1.7.0.1-1
- git-1.7.0.1

* Sat Feb 13 2010 Todd Zullinger <tmz@pobox.com> - 1.7.0-1
- git-1.7.0
- Link imap-send with libcrypto (#565147)
- Disable building of unused python remote helper libs

* Tue Jan 26 2010 Todd Zullinger <tmz@pobox.com> - 1.6.6.1-1
- git-1.6.6.1
- Use %%{gitcoredir}/git-daemon as xinetd server option, for SELinux (#529682)
- Make %%{_var}/lib/git the default gitweb projectroot (#556299)
- Include gitweb/INSTALL file as documentation, the gitweb README refers to it
- Ship a short example gitweb config file (%%{_sysconfdir}/gitweb.conf)
- Remove long fixed xinetd IPv6 workaround on Fedora (#557528)
- Install missing gitweb.js (#558740)

* Wed Dec 23 2009 Todd Zullinger <tmz@pobox.com> - 1.6.6-1
- git-1.6.6

* Fri Dec 11 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5.6-1
- git-1.6.5.6

* Sun Dec 06 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5.5-1
- git-1.6.5.5

* Fri Dec  4 2009 Stepan Kasal <skasal@redhat.com> - 1.6.5.3-2
- rebuild against perl 5.10.1

* Sat Nov 21 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5.3-1
- git-1.6.5.3
- Only BR perl(Error) on Fedora and RHEL >= 5
- Use config.mak to set build options
- Improve compatibility with EPEL
- Replace $RPM_BUILD_ROOT with %%{buildroot}
- Fix Obsoletes for those rebuilding on EL-4

* Mon Oct 26 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5.2-1
- git-1.6.5.2
- Drop asciidoc --unsafe option, it should not be needed anymore
- Don't use install -t/-T, they're not compatible with older coreutils
- Don't use -perm /a+x with find, it's incompatible with older findutils

* Sat Oct 17 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5.1-1
- git-1.6.5.1

* Sun Oct 11 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5-1
- git-1.6.5

* Mon Sep 28 2009 Todd Zullinger <tmz@pobox.com> - 1.6.5-0.2.rc2
- git-1.6.5.rc2
- Enable Linus' block-sha1 implementation

* Wed Sep 16 2009 Todd Zullinger <tmz@pobox.com> - 1.6.4.4-1
- git-1.6.4.4

* Sun Sep 13 2009 Todd Zullinger <tmz@pobox.com> - 1.6.4.3-1
- git-1.6.4.3

* Sun Aug 30 2009 Todd Zullinger <tmz@pobox.com> - 1.6.4.2-1
- git-1.6.4.2

* Sat Aug 22 2009 Todd Zullinger <tmz@pobox.com> - 1.6.4.1-1
- git-1.6.4.1

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.6.4-2
- rebuilt with new openssl

* Wed Jul 29 2009 Todd Zullinger <tmz@pobox.com> - 1.6.4-1
- git-1.6.4

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Jun 28 2009 Todd Zullinger <tmz@pobox.com> - 1.6.3.3-1
- git-1.6.3.3
- Move contributed hooks to %%{_datadir}/git-core/contrib/hooks (bug 500137)
- Fix rpmlint warnings about Summary and git-mergetool--lib missing shebang

* Fri Jun 19 2009 Todd Zullinger <tmz@pobox.com> - 1.6.3.2-3
- Temporarily disable asciidoc's safe mode until bug 506953 is fixed

* Fri Jun 19 2009 Todd Zullinger <tmz@pobox.com> - 1.6.3.2-2
- Fix git-daemon hang on invalid input (CVE-2009-2108, bug 505761)

* Fri Jun 05 2009 Todd Zullinger <tmz@pobox.com> - 1.6.3.2-1
- git-1.6.3.2
- Require emacs >= 22.2 for emacs support (bug 495312)
- Add a .desktop file for git-gui (bug 498801)
- Set ASCIIDOC8 and ASCIIDOC_NO_ROFF to correct documentation issues,
  the sed hack to fix bug 485161 should no longer be needed
- Escape newline in git-daemon xinetd description (bug 502393)
- Add xinetd to git-daemon Requires (bug 504105)
- Organize BuildRequires/Requires, drop redundant expat Requires
- Only build noarch subpackages on Fedora >= 10
- Only build emacs and arch subpackages on Fedora
- Handle curl/libcurl naming for EPEL and Fedora

* Fri Apr 03 2009 Todd Zullinger <tmz@pobox.com> - 1.6.2.2-1
- git-1.6.2.2
- Include contrib/ dir in %%doc (bug 492490)
- Don't set DOCBOOK_XSL_172, fix the '\&.ft' with sed (bug 485161)
- Ignore Branches output from cvsps-2.2b1 (bug 490602)
- Remove shebang from bash-completion script
- Include README in gitweb subpackage

* Mon Mar 09 2009 Todd Zullinger <tmz@pobox.com> - 1.6.2-1
- git-1.6.2
- Include contrib/emacs/README in emacs subpackage
- Drop upstreamed git-web--browse patch

* Tue Feb 24 2009 Todd Zullinger <tmz@pobox.com> - 1.6.1.3-2
- Require perl(Authen::SASL) in git-email (bug 483062)
- Build many of the subpackages as noarch
- Update URL field

* Mon Feb 09 2009 Todd Zullinger <tmz@pobox.com> 1.6.1.3-1
- git-1.6.1.3
- Set htmldir so "git help -w <command>" works
- Patch git-web--browse to not use "/sbin/start" to browse
- Include git-daemon documentation in the git-daemon package

* Thu Jan 29 2009 Josh Boyer <jwboyer@gmail.com> 1.6.1.2-1
- git-1.6.1.2

* Mon Jan 26 2009 Todd Zullinger <tmz@pobox.com> 1.6.1.1-1
- git-1.6.1.1
- Make compile more verbose

* Fri Jan 16 2009 Tomas Mraz <tmraz@redhat.com> 1.6.1-2
- rebuild with new openssl

* Sat Jan 03 2009 Todd Zullinger <tmz@pobox.com> 1.6.1-1
- Install git-* commands in %%{_libexecdir}/git-core, the upstream default
- Remove libcurl from Requires, rpm will pick this up automatically
- Consolidate build/install options in %%make_git (Roland McGrath)
- Include DirectoryIndex in gitweb httpd-config (bug 471692)
- Define DOCBOOK_XSL_172 to fix minor manpage issues
- Rename %%{_var}/lib/git-daemon to %%{_var}/lib/git
- Preserve timestamps on installed files
- Quiet some rpmlint complaints
- Use macros more consistently

* Sat Dec 20 2008 Todd Zullinger <tmz@pobox.com> 1.6.0.6-1
- git-1.6.0.6
- Fixes a local privilege escalation bug in gitweb
  (http://article.gmane.org/gmane.comp.version-control.git/103624)
- Add gitk Requires to git-gui (bug 476308)

* Thu Dec 11 2008 Josh Boyer <jboyer@gmail.com> 1.6.0.5-1
- git-1.6.0.5

* Mon Nov 17 2008 Seth Vidal <skvidal at fedoraproject.org>
- switch from /srv/git to /var/lib/git-daemon for packaging rules compliance

* Fri Nov 14 2008 Josh Boyer <jwboyer@gmail.com> 1.6.0.4-1
- git-1.6.0.4

* Wed Oct 22 2008 Josh Boyer <jwboyer@gmail.com> 1.6.0.3-1
- git-1.6.0.3
- Drop curl requirement in favor of libcurl (bug 449388)
- Add requires for SMTP-SSL perl module to make git-send-email work (bug 443615)

* Thu Aug 28 2008 James Bowes <jbowes@redhat.com> 1.6.0.1-1
- git-1.6.0.1

* Thu Jul 24 2008 James Bowes <jbowes@redhat.com> 1.5.6-4
- git-1.5.6.4

* Thu Jun 19 2008 James Bowes <jbowes@redhat.com> 1.5.6-1
- git-1.5.6

* Tue Jun  3 2008 Stepan Kasal <skasal@redhat.com> 1.5.5.3-2
- use tar.bz2 instead of tar.gz

* Wed May 28 2008 James Bowes <jbowes@redhat.com> 1.5.5.3-1
- git-1.5.5.3

* Mon May 26 2008 James Bowes <jbowes@redhat.com> 1.5.5.2-1
- git-1.5.5.2

* Mon Apr 21 2008 James Bowes <jbowes@redhat.com> 1.5.5.1-1
- git-1.5.5.1

* Wed Apr 09 2008 James Bowes <jbowes@redhat.com> 1.5.5-1
- git-1.5.5

* Fri Apr 04 2008 James Bowes <jbowes@redhat.com> 1.5.4.5-3
- Remove the last two requires on git-core.

* Wed Apr 02 2008 James Bowes <jbowes@redhat.com> 1.5.4.5-2
- Remove a patch that's already upstream.

* Fri Mar 28 2008 James Bowes <jbowes@redhat.com> 1.5.4.5-1
- git-1.5.4.5

* Wed Mar 26 2008 James Bowes <jbowes@redhat.com> 1.5.4.4-4
- Own /etc/bash_completion.d in case bash-completion isn't installed.

* Tue Mar 25 2008 James Bowes <jbowes@redhat.com> 1.5.4.4-3
- Include the sample hooks from contrib/hooks as docs (bug 321151).
- Install the bash completion script from contrib (bug 433255).
- Include the html docs in the 'core' package again (bug 434271).

* Wed Mar 19 2008 James Bowes 1.5.4.4-2
- Obsolete git <= 1.5.4.3, to catch going from F8 to rawhide/F9

* Thu Mar 13 2008 James Bowes <jbowes@redhat.com> 1.5.4.4-1
- git-1.5.4.4

* Mon Mar  3 2008 Tom "spot" Callaway <tcallawa@redhat.com> 1.5.4.3-3
- rebuild for new perl (again)

* Sun Feb 24 2008 Bernardo Innocenti <bernie@codewiz.org> 1.5.4.3-2
- Do not silently overwrite /etc/httpd/conf.d/git.conf

* Sat Feb 23 2008 James Bowes <jbowes@redhat.com> 1.5.4.3-1
- git-1.5.4.3
- Include Kristian Høgsberg's changes to rename git-core to
  git and git to git-all.

* Sun Feb 17 2008 James Bowes <jbowes@redhat.com> 1.5.4.2-1
- git-1.5.4.2

* Mon Feb 11 2008 Jeremy Katz <katzj@redhat.com> - 1.5.4.1-2
- Add upstream patch (e62a641de17b172ffc4d3a803085c8afbfbec3d1) to have 
  gitweb rss feeds point be commitdiffs instead of commit

* Sun Feb 10 2008 James Bowes <jbowes@redhat.com> 1.5.4.1-1
- git-1.5.4.1

* Tue Feb 05 2008 Tom "spot" Callaway <tcallawa@redhat.com> 1.5.4-3
- rebuild for new perl

* Sun Feb 03 2008 James Bowes <jbowes@redhat.com> 1.5.4-1
- Add BuidRequires on gettext.

* Sat Feb 02 2008 James Bowes <jbowes@redhat.com> 1.5.4-1
- git-1.5.4

* Tue Jan 08 2008 James Bowes <jbowes@redhat.com> 1.5.3.8-1
- git-1.5.3.8

* Fri Dec 21 2007 James Bowes <jbowes@redhat.com> 1.5.3.7-2
- Have git metapackage require explicit versions (bug 247214)

* Mon Dec 03 2007 Josh Boyer <jwboyer@gmail.com> 1.5.3.7-1
- git-1.5.3.7

* Tue Nov 27 2007 Josh Boyer <jwboyer@gmail.com> 1.5.3.6-1
- git-1.5.3.6
- git-core requires perl(Error) (bug 367861)
- git-svn requires perl(Term:ReadKey) (bug 261361)
- git-email requires perl-Git (bug 333061)

* Wed Oct 24 2007 Lubomir Kundrak <lkundrak@redhat.com> 1.5.3.4-2
- git-Perl requires Error package

* Tue Oct 09 2007 James Bowes <jbowes@redhat.com> 1.5.3.4-1
- git-1.5.3.4

* Sun Sep 30 2007 James Bowes <jbowes@redhat.com> 1.5.3.3-1
- git-1.5.3.3

* Wed Sep 26 2007 James Bowes <jbowes@redhat.com> 1.5.3.2-1
- git-1.5.3.2

* Thu Sep 06 2007 Josh Boyer <jwboyer@jdub.homelinux.org> 1.5.3.1-2
- Include git-gui and git-citool docs

* Thu Sep 06 2007 Josh Boyer <jwboyer@jdub.homelinux.org> 1.5.3.1-1
- git-1.5.3.1-1

* Thu Aug 23 2007 James Bowes <jbowes@redhat.com> 1.5.2.5-1
- git-1.5.2.5-1

* Fri Aug 03 2007 Josh Boyer <jwboyer@jdub.homelinux.org> 1.5.2.4-1
- git-1.5.2.4-1

* Tue Jul 03 2007 Josh Boyer <jwboyer@jdub.homelinux.org> 1.5.2.2-3
- Add git-daemon and gitweb packages

* Thu Jun 21 2007 Josh Boyer <jwboyer@jdub.homelinux.org> 1.5.2.2-2
- Add emacs-git package (#235431)

* Mon Jun 18 2007 James Bowes <jbowes@redhat.com> 1.5.2.2-1
- git-1.5.2.2

* Fri Jun 08 2007 James Bowes <jbowes@redhat.com> 1.5.2.1-1
- git-1.5.2.1

* Sun May 13 2007 Quy Tonthat <qtonthat@gmail.com>
- Added lib files for git-gui
- Added Documentation/technical (As needed by Git Users Manual)

* Tue May 8 2007 Quy Tonthat <qtonthat@gmail.com>
- Added howto files

* Fri Mar 30 2007 Chris Wright <chrisw@redhat.com> 1.5.0.6-1
- git-1.5.0.6

* Mon Mar 19 2007 Chris Wright <chrisw@redhat.com> 1.5.0.5-1
- git-1.5.0.5

* Tue Mar 13 2007 Chris Wright <chrisw@redhat.com> 1.5.0.3-1
- git-1.5.0.3

* Fri Mar 2 2007 Chris Wright <chrisw@redhat.com> 1.5.0.2-2
- BuildRequires perl-devel as of perl-5.8.8-14 (bz 230680)

* Mon Feb 26 2007 Chris Wright <chrisw@redhat.com> 1.5.0.2-1
- git-1.5.0.2

* Tue Feb 13 2007 Nicolas Pitre <nico@cam.org>
- Update core package description (Git isn't as stupid as it used to be)

* Mon Feb 12 2007 Junio C Hamano <junkio@cox.net>
- Add git-gui and git-citool.

* Sun Dec 10 2006 Chris Wright <chrisw@redhat.com> 1.4.4.2-2
- no need to install manpages executable (bz 216790)
- use bytes for git-cvsserver

* Sun Dec 10 2006 Chris Wright <chrisw@redhat.com> 1.4.4.2-1
- git-1.4.4.2

* Mon Nov 6 2006 Jindrich Novy <jnovy@redhat.com> 1.4.2.4-2
- rebuild against the new curl

* Tue Oct 17 2006 Chris Wright <chrisw@redhat.com> 1.4.2.4-1
- git-1.4.2.4

* Wed Oct 4 2006 Chris Wright <chrisw@redhat.com> 1.4.2.3-1
- git-1.4.2.3

* Fri Sep 22 2006 Chris Wright <chrisw@redhat.com> 1.4.2.1-1
- git-1.4.2.1

* Mon Sep 11 2006 Chris Wright <chrisw@redhat.com> 1.4.2-1
- git-1.4.2

* Thu Jul 6 2006 Chris Wright <chrisw@redhat.com> 1.4.1-1
- git-1.4.1

* Tue Jun 13 2006 Chris Wright <chrisw@redhat.com> 1.4.0-1
- git-1.4.0

* Thu May 4 2006 Chris Wright <chrisw@redhat.com> 1.3.3-1
- git-1.3.3
- enable git-email building, prereqs have been relaxed

* Thu May 4 2006 Chris Wright <chrisw@redhat.com> 1.3.2-1
- git-1.3.2

* Fri Apr 28 2006 Chris Wright <chrisw@redhat.com> 1.3.1-1
- git-1.3.1

* Wed Apr 19 2006 Chris Wright <chrisw@redhat.com> 1.3.0-1
- git-1.3.0

* Mon Apr 10 2006 Chris Wright <chrisw@redhat.com> 1.2.6-1
- git-1.2.6

* Wed Apr 5 2006 Chris Wright <chrisw@redhat.com> 1.2.5-1
- git-1.2.5

* Wed Mar 1 2006 Chris Wright <chrisw@redhat.com> 1.2.4-1
- git-1.2.4

* Wed Feb 22 2006 Chris Wright <chrisw@redhat.com> 1.2.3-1
- git-1.2.3

* Tue Feb 21 2006 Chris Wright <chrisw@redhat.com> 1.2.2-1
- git-1.2.2

* Thu Feb 16 2006 Chris Wright <chrisw@redhat.com> 1.2.1-1
- git-1.2.1

* Mon Feb 13 2006 Chris Wright <chrisw@redhat.com> 1.2.0-1
- git-1.2.0

* Wed Feb 1 2006 Chris Wright <chrisw@redhat.com> 1.1.6-1
- git-1.1.6

* Tue Jan 24 2006 Chris Wright <chrisw@redhat.com> 1.1.4-1
- git-1.1.4

* Sun Jan 15 2006 Chris Wright <chrisw@redhat.com> 1.1.2-1
- git-1.1.2

* Tue Jan 10 2006 Chris Wright <chrisw@redhat.com> 1.1.1-1
- git-1.1.1

* Tue Jan 10 2006 Chris Wright <chrisw@redhat.com> 1.1.0-1
- Update to latest git-1.1.0 (drop git-email for now)
- Now creates multiple packages:
-        git-core, git-svn, git-cvs, git-arch, gitk

* Mon Nov 14 2005 H. Peter Anvin <hpa@zytor.com> 0.99.9j-1
- Change subpackage names to git-<name> instead of git-core-<name>
- Create empty root package which brings in all subpackages
- Rename git-tk -> gitk

* Thu Nov 10 2005 Chris Wright <chrisw@osdl.org> 0.99.9g-1
- zlib dependency fix
- Minor cleanups from split
- Move arch import to separate package as well

* Tue Sep 27 2005 Jim Radford <radford@blackbean.org>
- Move programs with non-standard dependencies (svn, cvs, email)
  into separate packages

* Tue Sep 27 2005 H. Peter Anvin <hpa@zytor.com>
- parallelize build
- COPTS -> CFLAGS

* Fri Sep 16 2005 Chris Wright <chrisw@osdl.org> 0.99.6-1
- update to 0.99.6

* Fri Sep 16 2005 Horst H. von Brand <vonbrand@inf.utfsm.cl>
- Linus noticed that less is required, added to the dependencies

* Sun Sep 11 2005 Horst H. von Brand <vonbrand@inf.utfsm.cl>
- Updated dependencies
- Don't assume manpages are gzipped

* Thu Aug 18 2005 Chris Wright <chrisw@osdl.org> 0.99.4-4
- drop sh_utils, sh-utils, diffutils, mktemp, and openssl Requires
- use RPM_OPT_FLAGS in spec file, drop patch0

* Wed Aug 17 2005 Tom "spot" Callaway <tcallawa@redhat.com> 0.99.4-3
- use dist tag to differentiate between branches
- use rpm optflags by default (patch0)
- own %%{_datadir}/git-core/

* Mon Aug 15 2005 Chris Wright <chrisw@osdl.org>
- update spec file to fix Buildroot, Requires, and drop Vendor

* Sun Aug 07 2005 Horst H. von Brand <vonbrand@inf.utfsm.cl>
- Redid the description
- Cut overlong make line, loosened changelog a bit
- I think Junio (or perhaps OSDL?) should be vendor...

* Thu Jul 14 2005 Eric Biederman <ebiederm@xmission.com>
- Add the man pages, and the --without docs build option

* Thu Jul 7 2005 Chris Wright <chris@osdl.org>
- initial git spec file
