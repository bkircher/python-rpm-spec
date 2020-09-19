"""Python module for parsing RPM spec files.

RPMs are build from a package's sources along with a spec file. The spec file controls how the RPM
is built. This module allows you to parse spec files and gives you simple access to various bits of
information that is contained in the spec file.

Current status: This module does not parse everything of a spec file. Only the pieces I needed. So
there is probably still plenty of stuff missing. However, it should not be terribly complicated to
add support for the missing pieces.

"""

import re
from abc import ABCMeta, abstractmethod

__all__ = ["Spec", "replace_macros", "Package"]


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
        if context["current_subpackage"] is not None:
            target_obj = context["current_subpackage"]
        return target_obj


class _NameValue(_Tag):
    """Parse a simple name → value tag."""

    def __init__(self, name, pattern_obj, attr_type=None):
        super().__init__(name, pattern_obj, attr_type if attr_type else str)

    def update_impl(self, spec_obj, context, match_obj, line):
        target_obj = _Tag.current_target(spec_obj, context)
        value = match_obj.group(1)

        # Sub-packages
        if self.name == "name":
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
        spec_obj.macros[name] = str(value)
        if name not in _tag_names:
            # Also make available as attribute of spec object
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
        if self.name == "packages":
            if value == "-n":
                subpackage_name = line.rsplit(" ", 1)[-1].rstrip()
            else:
                subpackage_name = "{}-{}".format(spec_obj.name, value)
            package = Package(subpackage_name)
            context["current_subpackage"] = package
            package.is_subpackage = True
            spec_obj.packages.append(package)
        elif self.name in [
            "build_requires",
            "requires",
            "conflicts",
            "obsoletes",
            "provides",
        ]:
            # Macros are valid in requirements
            value = replace_macros(value, spec=spec_obj)

            # It's also legal to do:
            #   Requires: a b c
            #   Requires: b >= 3.1
            #   Requires: a, b >= 3.1, c

            # 1. Tokenize
            tokens = [val for val in re.split("[\t\n, ]", value) if val != ""]
            values = []

            # 2. Join
            add = False
            for val in tokens:
                if add:
                    add = False
                    val = values.pop() + " " + val
                elif val in [">=", "!=", ">", "<", "<=", "==", "="]:
                    add = True  # Add next value to this one
                    val = values.pop() + " " + val
                values.append(val)

            for val in values:
                requirement = Requirement(val)
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
        dictionary = getattr(spec_obj, "{}_dict".format(self.name))
        dictionary[source_name] = value
        target_obj = _Tag.current_target(spec_obj, context)
        getattr(target_obj, self.name).append(value)
        return spec_obj, context


def re_tag_compile(tag):
    return re.compile(tag, re.IGNORECASE)


_tags = [
    _NameValue("name", re_tag_compile(r"^Name\s*:\s*(\S+)")),
    _NameValue("version", re_tag_compile(r"^Version\s*:\s*(\S+)")),
    _NameValue("epoch", re_tag_compile(r"^Epoch\s*:\s*(\S+)")),
    _NameValue("release", re_tag_compile(r"^Release\s*:\s*(\S+)")),
    _NameValue("summary", re_tag_compile(r"^Summary\s*:\s*(.+)")),
    _NameValue("license", re_tag_compile(r"^License\s*:\s*(.+)")),
    _NameValue("group", re_tag_compile(r"^Group\s*:\s*(.+)")),
    _NameValue("url", re_tag_compile(r"^URL\s*:\s*(\S+)")),
    _NameValue("buildroot", re_tag_compile(r"^BuildRoot\s*:\s*(\S+)")),
    _NameValue("buildarch", re_tag_compile(r"^BuildArch\s*:\s*(\S+)")),
    _ListAndDict("sources", re_tag_compile(r"^(Source\d*\s*):\s*(.+)")),
    _ListAndDict("patches", re_tag_compile(r"^(Patch\d*\s*):\s*(\S+)")),
    _List("build_requires", re_tag_compile(r"^BuildRequires\s*:\s*(.+)")),
    _List("requires", re_tag_compile(r"^Requires\s*:\s*(.+)")),
    _List("conflicts", re_tag_compile(r"^Conflicts\s*:\s*(.+)")),
    _List("obsoletes", re_tag_compile(r"^Obsoletes\s*:\s*(.+)")),
    _List("provides", re_tag_compile(r"^Provides\s*:\s*(.+)")),
    _List("packages", re.compile(r"^%package\s+(\S+)")),
    _MacroDef("define", re.compile(r"^%define\s+(\S+)\s+(\S+)")),
    _MacroDef("global", re.compile(r"^%global\s+(\S+)\s+(\S+)")),
]

_tag_names = [tag.name for tag in _tags]

_macro_pattern = re.compile(r"%{(\S+?)\}")


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

    expr = re.compile(r"(.*?)\s+([<>]=?|=)\s+(\S+)")

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
            if tag.attr_type is list and tag.name in [
                "build_requires",
                "requires",
                "conflicts",
                "obsoletes",
                "provides",
            ]:
                setattr(self, tag.name, tag.attr_type())

        self.name = name
        self.is_subpackage = False

    def __repr__(self):
        return "Package('{}')".format(self.name)


class Spec:
    """Represents a single spec file."""

    def __init__(self):
        for tag in _tags:
            if tag.attr_type is list:
                setattr(self, tag.name, tag.attr_type())
            else:
                setattr(self, tag.name, None)

        self.sources_dict = {}
        self.patches_dict = {}
        self.macros = {}

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
        with open(filename, "r", encoding="utf-8") as f:
            parse_context = {"current_subpackage": None}
            for line in f:
                spec, parse_context = _parse(spec, parse_context, line)
        return spec

    @staticmethod
    def from_string(string: str):
        """Creates a new Spec object from a given string.

        :param string: The contents of a spec file.
        :return: A new Spec object.
        """

        spec = Spec()
        parse_context = {"current_subpackage": None}
        for line in string.splitlines():
            spec, parse_context = _parse(spec, parse_context, line)
        return spec


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
            assert parts
            if _test_conditional(macro_name):
                if hasattr(spec, parts[0]) or parts[0] in spec.macros:
                    if len(parts) == 2:
                        return parts[1]

                    return spec.macros.get(parts[0], getattr(spec, parts[0], None))

                return ""

            if not hasattr(spec, parts[0]) and parts[0] not in spec.macros:
                if len(parts) == 2:
                    return parts[1]

                return spec.macros.get(parts[0], getattr(spec, parts[0], None))

            return ""

        if spec:
            value = spec.macros.get(macro_name, getattr(spec, macro_name, None))
            if value:
                return str(value)
        return match.string[match.start() : match.end()]

    # Recursively expand macros
    # Note: If macros are not defined in the spec file, this won't try to
    # expand them.
    while True:
        ret = re.sub(_macro_pattern, _macro_repl, string)
        if ret != string:
            string = ret
            continue
        return ret
