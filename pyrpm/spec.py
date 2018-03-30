"""Python module for parsing RPM spec files.

RPMs are build from a package's sources along with a spec file. The spec file controls how the RPM
is built. This module allows you to parse spec files and gives you simple access to various bits of
information that is contained in the spec file.

Current status: This module does not parse everything of a spec file. Only the pieces I needed. So
there is probably still plenty of stuff missing. However, it should not be terribly complicated to
add support for the missing pieces.

"""

import re, os
from abc import (ABCMeta, abstractmethod)

__all__ = ['Spec', 'replace_macros', 'Package']


class _Tag(metaclass=ABCMeta):
    def __init__(self, name, pattern_obj, attr_type):
        self.name = name
        self.pattern_obj = pattern_obj
        self.attr_type = attr_type

    def test(self, line):
        return re.search(self.pattern_obj, line)

    def update(self, spec_obj, context, match_obj, line):
        """Update given spec object and parse context and return them again.

        :param spec_obj: An instance of Spec class
        :param context: The parse context
        :param match_obj: The re.match object
        :param line: The original line
        :return: Given updated Spec instance and parse context dictionary.
        """

        assert spec_obj
        assert context
        assert match_obj
        assert line

        return self.update_impl(spec_obj, context, match_obj, line)

    @abstractmethod
    def update_impl(self, spec_obj, context, match_obj, line):
        pass

    @staticmethod
    def current_target(spec_obj, context):
        target_obj = spec_obj
        if context['current_subpackage'] is not None:
            target_obj = context['current_subpackage']
        return target_obj


class _NameValue(_Tag):
    """Parse a simple name → value tag."""

    def __init__(self, name, pattern_obj, attr_type=None):
        super().__init__(name, pattern_obj, attr_type if attr_type else str)

    def update_impl(self, spec_obj, context, match_obj, line):
        target_obj = _Tag.current_target(spec_obj, context)
        value = match_obj.group(1)

        # Sub-packages
        if self.name == 'name':
            spec_obj.packages = []
            spec_obj.packages.append(Package(value))

        setattr(target_obj, self.name, self.attr_type(value))
        return spec_obj, context


class _MacroDef(_Tag):
    """Parse global macro definitions."""

    def __init__(self, name, pattern_obj):
        super().__init__(name, pattern_obj, str)

    def update_impl(self, spec_obj, context, match_obj, line):
        name, value = match_obj.groups()
        setattr(spec_obj, name, str(value))
        return spec_obj, context


class _List(_Tag):
    """Parse a tag that expands to a list."""

    def __init__(self, name, pattern_obj):
        super().__init__(name, pattern_obj, list)

    def update_impl(self, spec_obj, context, match_obj, line):
        target_obj = _Tag.current_target(spec_obj, context)

        if not hasattr(target_obj, self.name):
            setattr(target_obj, self.name, list())

        value = match_obj.group(1)
        if self.name == 'packages':
            if value == '-n':
                subpackage_name = line.rsplit(' ', 1)[-1].rstrip()
            else:
                subpackage_name = '{}-{}'.format(spec_obj.name, value)
            package = Package(subpackage_name)
            context['current_subpackage'] = package
            package.is_subpackage = True
            spec_obj.packages.append(package)
        elif self.name in ['requires', 'build_requires']:
            requirement = Requirement(value)
            getattr(target_obj, self.name).append(requirement)
        else:
            getattr(target_obj, self.name).append(value)

        return spec_obj, context


class _ListAndDict(_Tag):
    """Parse a tag that expands to a list and to a dict."""

    def __init__(self, name, pattern_obj):
        super().__init__(name, pattern_obj, list)

    def update_impl(self, spec_obj, context, match_obj, line):
        source_name, value = match_obj.groups()
        dictionary = getattr(spec_obj, '{}_dict'.format(self.name))
        dictionary[source_name] = value
        target_obj = _Tag.current_target(spec_obj, context)
        getattr(target_obj, self.name).append(value)
        return spec_obj, context


_tags = [
    _NameValue('name', re.compile(r'^Name:\s*(\S+)')),
    _NameValue('version', re.compile(r'^Version:\s*(\S+)')),
    _NameValue('epoch', re.compile(r'^Epoch:\s*(\S+)'), attr_type=int),
    _NameValue('release', re.compile(r'^Release:\s*(\S+)')),
    _NameValue('summary', re.compile(r'^Summary:\s*(.+)')),
    _NameValue('license', re.compile(r'^License:\s*(.+)')),
    _NameValue('group', re.compile(r'^Group:\s*(\S+)')),
    _NameValue('url', re.compile(r'^URL:\s*(\S+)')),
    _NameValue('buildroot', re.compile(r'^BuildRoot:\s*(\S+)')),
    _NameValue('buildarch', re.compile(r'^BuildArch:\s*(\S+)')),
    _ListAndDict('sources', re.compile(r'^(Source\d*):\s*(\S+)')),
    _ListAndDict('patches', re.compile(r'^(Patch\d*):\s*(\S+)')),
    _List('build_requires', re.compile(r'^BuildRequires:\s*(.+)')),
    _List('requires', re.compile(r'^Requires:\s*(.+)')),
    _List('requires_post', re.compile(r'^Requires\(post\):\s*(.+)')),
    _List('provides', re.compile(r'^Provides:\s*(.+)')),
    _List('packages', re.compile(r'^%package\s+(\S+)')),
    _List('files', re.compile(r'%attr\(.*\)\s+(\S+)')),
    _MacroDef('define', re.compile(r'^%define\s+(\S+)\s+(\S+)')),
    _MacroDef('global', re.compile(r'^%global\s+(\S+)\s+(\S+)'))
]

_macro_pattern = re.compile(r'%{(\S+?)\}')


def _parse(spec_obj, context, line):
    for tag in _tags:
        match = tag.test(line)
        if match:
            return tag.update(spec_obj, context, match, line)
    return spec_obj, context


class Requirement:
    """Represents a single requirement or build requirement in an RPM spec file.

    Each spec file contains one or more requirements or build requirements. 
    For example, consider following spec file::

        Name:           foo
        Version:        0.1

        %description
        %{name} is the library that everyone needs.

        %package devel
        Summary: Header files, libraries and development documentation for %{name}
        Group: Development/Libraries
        Requires: %{name}%{?_isa} = %{version}-%{release}
        BuildRequires: gstreamer%{?_isa} >= 0.1.0

        %description devel
        This package contains the header files, static libraries, and development
        documentation for %{name}. If you like to develop programs using %{name}, you
        will need to install %{name}-devel.

    This spec file's requirements have a name and either a required or minimum
    version.
    """
    expr = re.compile(r'(.*?)\s+([<>]=?|=)\s+(\S+)')

    def __init__(self, name):
        assert isinstance(name, str)
        self.line = name
        match = Requirement.expr.match(name)
        if match:
            self.name = match.group(1)
            self.operator = match.group(2)
            self.version = match.group(3)
        else:
            self.name = name
            self.operator = None
            self.version = None

    def __repr__(self):
        return self.line


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

        for tag in _tags:
            if tag.attr_type is list and tag.name in ["build_requires", "requires", "conflicts", "obsoletes",
                                                      "provides"]:
                setattr(self, tag.name, tag.attr_type())

        self.name = name
        self.is_subpackage = False

    def __repr__(self):
        return "Package('{}')".format(self.name)


class Spec:
    """Represents a single spec file.

    """

    def __init__(self):
        for tag in _tags:
            if tag.attr_type is list:
                setattr(self, tag.name, tag.attr_type())
            else:
                setattr(self, tag.name, None)

        self.sources_dict = dict()
        self.patches_dict = dict()

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
        str = open(filename, 'r', encoding='utf-8').read()
        return Spec.from_string(str, os.path.dirname(os.path.abspath(filename)))

    @staticmethod
    def from_string(string: str, relpath: str):
        """Creates a new Spec object from a given string.

        :param string: The contents of a spec file.
        :param relpath: The relative path to use for expanding include directives
        :return: A new Spec object.
        """

        spec = Spec()
        parse_context = {
            'current_subpackage': None
        }

        # first pass: expand the "%include" lines:
        content_lines = Spec.__resolve_includes(string.splitlines(), relpath)
        
        # second pass: parse the SPEC file:
        for line in content_lines:
            spec, parse_context = _parse(spec, parse_context, line)
        return spec

    @staticmethod
    def __resolve_includes(content_lines, relpath):
        include_pattern = re.compile(r'^%include\s+(\S+)')
        while True:
            restart_processing = False
            
            for nline in range(0,len(content_lines)):
                line = content_lines[nline]
                #print("Processing line", line)
                match = include_pattern.match(line)
                if match:
                    filename = match.group(1)
                    
                    #print("  *** At line {} found inclusion of file: {} in range {}-{}".format(nline, filename, match.start(), match.end()))
                    included_content = open(os.path.join(relpath,filename), 'r', encoding='utf-8').read()
                    
                    # remove the current line and replace it with included content:
                    del content_lines[nline]
                    content_lines[nline:nline] = included_content.splitlines()
                    restart_processing = True
                    break

                if restart_processing:
                    break
                nline = nline+1
                    
            if not restart_processing:
                break       # no need of another pass
        return content_lines

def replace_macros(string, spec=None):
    """Replace all macros in given string with corresponding values.

    For example: a string '%{name}-%{version}.tar.gz' will be transformed to 'foo-2.0.tar.gz'.

    :param string A string containing macros that you want to be replaced
    :param spec An optional spec file. If given, definitions in that spec
    file will be used to replace macros.

    :return A string where all macros in given input are substituted as good as possible.

    """
    if spec:
        assert isinstance(spec, Spec)

    def _is_conditional(macro: str) -> bool:
        return macro.startswith("?") or macro.startswith("!")

    def _test_conditional(macro: str) -> bool:
        if macro[0] == "?":
            return True
        if macro[0] == "!":
            return False
        raise Exception("Given string is not a conditional macro")

    def _macro_repl(match):
        macro_name = match.group(1)
        if _is_conditional(macro_name) and spec:
            parts = macro_name[1:].split(sep=":", maxsplit=1)
            assert len(parts) > 0
            if _test_conditional(macro_name):  # ?
                if hasattr(spec, parts[0]):
                    if len(parts) == 2:
                        return parts[1]
                    else:
                        return getattr(spec, parts[0], None)
                else:
                    return ""
            else:  # !
                if not hasattr(spec, parts[0]):
                    if len(parts) == 2:
                        return parts[1]
                    else:
                        return getattr(spec, parts[0], None)
                else:
                    return ""

        if spec:
            value = getattr(spec, macro_name, None)
            if value:
                return str(value)
        return match.string[match.start():match.end()]

    return re.sub(_macro_pattern, _macro_repl, string)
