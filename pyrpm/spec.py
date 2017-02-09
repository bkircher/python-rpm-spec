"""Python module for parsing RPM spec files.

RPMs are build from a package's sources along with a spec file. The spec file controls how the RPM
is built. This module allows you to parse spec files and gives you simple access to various bits of
information that is contained in the spec file.

Current status: This module does not parse everything of a spec file. Only the pieces I needed. So
there is probably still plenty of stuff missing. However, it should not be terribly complicated to
add support for the missing pieces.

"""

import re

__all__ = ['Spec', 'replace_macros', 'Package']

_tags = {
    'name': (str, re.compile(r'^Name:\s*(\S+)')),
    'version': (str, re.compile(r'^Version:\s*(\S+)')),
    'epoch': (int, re.compile(r'^Epoch:\s*(\S+)')),
    'release': (str, re.compile(r'^Release:\s*(\S+)')),
    'summary': (str, re.compile(r'^Summary:\s*(.+)')),
    'license': (str, re.compile(r'^License:\s*(.+)')),
    'group': (str, re.compile(r'^Group:\s*(\S+)')),
    'url': (str, re.compile(r'^URL:\s*(\S+)')),
    'buildroot': (str, re.compile(r'^BuildRoot:\s*(\S+)')),
    'buildarch': (str, re.compile(r'^BuildArch:\s*(\S+)')),
    'sources': (list, re.compile(r'^Source\d*:\s*(\S+)')),
    'patches': (list, re.compile(r'^Patch\d*:\s*(\S+)')),
    'build_requires': (list, re.compile(r'^BuildRequires:\s*(.+)')),
    'requires': (list, re.compile(r'^Requires:\s*(.+)')),
    'packages': (list, re.compile(r'^%package\s+(\S+)'))
}

_macro_pattern = re.compile(r'%\{(\S+?)\}')


def _parse(spec_obj, context, line):
    for name, value in _tags.items():
        attr_type, regex = value
        match = re.search(regex, line)
        if match:
            tag_value = match.group(1)

            if name == 'name':
                spec_obj.packages = []
                spec_obj.packages.append(Package(tag_value))

            target_obj = spec_obj
            if context['current_subpackage'] is not None:
                target_obj = context['current_subpackage']

            if attr_type is list:
                if not hasattr(target_obj, name):
                    setattr(target_obj, name, list())

                if name == 'packages':
                    if tag_value == '-n':
                        subpackage_name = line.rsplit(' ', 1)[-1].rstrip()
                    else:
                        subpackage_name = '{}-{}'.format(spec_obj.name, tag_value)
                    package = Package(subpackage_name)
                    context['current_subpackage'] = package
                    package.is_subpackage = True
                    spec_obj.packages.append(package)
                else:
                    getattr(target_obj, name).append(tag_value)
            else:
                setattr(target_obj, name, attr_type(tag_value))
    return spec_obj, context


class Package:
    """Represents a single package in a RPM spec file.

    Each spec file describes at least one package and can contain one or more subpackages (described
    by the %package directive). For example, consider following spec file::

        Name:           foo
        Version:        0.1

        %description
        %{name} is the library that everyone needs.

        %package devel
        Summary: Header files, libraries and development documentation for %{name}
        Group: Development/Libraries
        Requires: %{name}%{?_isa} = %{version}-%{release}

        %description devel
        This package contains the header files, static libraries, and development
        documentation for %{name}. If you like to develop programs using %{name}, you
        will need to install %{name}-devel.

        %package -n bar
        Summary: A command line client for foo.
        License: GPLv2+

        %description -n bar
        This package contains a command line client for foo.

    This spec file will create three packages:

    * A package named foo, the base package.
    * A package named foo-devel, a subpackage.
    * A package named bar, also a subpackage, but without the foo- prefix.

    As you can see above, the name of a subpackage normally includes the main package name. When the
    -n option is added to the %package directive, the prefix of the base package name is omitted and
    a completely new name is used.

    """

    def __init__(self, name):
        assert isinstance(name, str)

        self.name = name
        self.is_subpackage = False

    def __repr__(self):
        return "Package('{}')".format(self.name)


class Spec:
    """Represents a single spec file.

    """

    @property
    def packages_dict(self):
        """All packages in this RPM spec as a dictionary.

        You can access the individual packages by their package name, e.g.,

        git_spec.packages_dict['git-doc']

        """
        assert self.packages
        return dict(zip([package.name for package in self.packages], self.packages))

    @staticmethod
    def from_file(filename):
        """Creates a new Spec object from a given file.

        :param filename: The path to the spec file.
        :return: A new Spec object.
        """

        spec = Spec()
        with open(filename, 'r', encoding='utf-8') as f:
            parse_context = {
                'current_subpackage': None
            }
            for line in f:
                spec, parse_context = _parse(spec, parse_context, line)
        return spec


def replace_macros(string, spec=None):
    """Replace all macros in given string with corresponding values.

    For example: a string '%{name}-%{version}.tar.gz' will be transformed to 'foo-2.0.tar.gz'.

    TODO: There is also `rpm --eval "%{macro}"` which could give us the expanded definition of a
    macro. Useful for macros that are global, e.g. %{_build_arch}.

    :return A string where all macros in given input are substituted as good as possible.

    """
    if spec:
        assert isinstance(spec, Spec)

    def _macro_repl(match):
        attr_name = match.group(1)
        if spec:
            value = getattr(spec, attr_name, None)
            if value:
                return str(value)
        return match.string[match.start():match.end()]

    return re.sub(_macro_pattern, _macro_repl, string)
