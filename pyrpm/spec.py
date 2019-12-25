"""Python module for parsing RPM spec files.

RPMs are build from a package's sources along with a spec file. The spec file controls how the RPM
is built. This module allows you to parse spec files and gives you simple access to various bits of
information that is contained in the spec file.

Current status: This module does not parse everything of a spec file. Only the pieces I needed. So
there is probably still plenty of stuff missing. However, it should not be terribly complicated to
add support for the missing pieces.

"""

import typing
from abc import ABCMeta, abstractmethod
import re
from functools import partial
import argparse
from warnings import warn
from pathlib import Path

__all__ = ["Spec", "replace_macros", "Package"]


class _Tag(metaclass=ABCMeta):
    def __init__(self, name: str, pattern_obj: re.Pattern, attr_type: type) -> None:
        self.name = name
        self.pattern_obj = pattern_obj
        self.attr_type = attr_type

    def test(self, line: str) -> typing.Optional[re.Match]:
        return re.search(self.pattern_obj, line)

    def update(self, spec_obj: "Spec", context: typing.Dict[str, typing.Any], match_obj: re.Match, line: str) -> typing.Any:
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
    def current_target(spec_obj: "Spec", context: typing.Dict[str, typing.Any]) -> typing.Union["Spec", "Package"]:
        target_obj = spec_obj
        if context["current_subpackage"] is not None:
            target_obj = context["current_subpackage"]
        return target_obj


class _NameValue(_Tag):
    """Parse a simple name → value tag."""

    def __init__(self, name: str, pattern_obj: re.Pattern, attr_type: typing.Optional[type] = None) -> None:
        super().__init__(name, pattern_obj, attr_type if attr_type else str)

    def update_impl(self, spec_obj: "Spec", context: typing.Dict[str, typing.Any], match_obj: re.Match, line: str) -> typing.Tuple["Spec", dict]:
        target_obj = _Tag.current_target(spec_obj, context)
        value = match_obj.group(1)

        # Sub-packages
        if self.name == "name":
            spec_obj.packages = []
            spec_obj.packages.append(Package(value))

        setattr(target_obj, self.name, self.attr_type(value))
        return spec_obj, context

class _SetterMacroDef(_Tag):
    """Parse global macro definitions."""

    def __init__(self, name: str, pattern_obj: re.Pattern) -> None:
        super().__init__(name, pattern_obj, str)
    
    def getNamespace(self, spec_obj, context):
        raise NotImplementedError()

    def update_impl(self, spec_obj: "Spec", context: typing.Dict[str, typing.Any], match_obj: re.Match, line: str) -> typing.Tuple["Spec", dict]:
        name, value = match_obj.groups()
        setattr(self.getNamespace(spec_obj, context), name, str(value))
        return spec_obj, context

class _GlobalMacroDef(_SetterMacroDef):
    """Parse global macro definitions."""

    def getNamespace(self, spec_obj: "Spec", context: typing.Dict[str, typing.Any]) -> "Spec":
        return spec_obj

class _LocalMacroDef(_SetterMacroDef):
    """Parse define macro definitions."""

    def getNamespace(self, spec_obj: "Spec", context: typing.Dict[str, typing.Any]) -> "Spec":
        return context["current_subpackage"]


class _MacroDef(_Tag):
    """Parse global macro definitions."""

    def __init__(self, name, pattern_obj):
        super().__init__(name, pattern_obj, str)

    def update_impl(self, spec_obj, context, match_obj, line):
        name, value = match_obj.groups()
        setattr(spec_obj, name, str(value))
        context["line_processor"] = None
        return spec_obj, context


class _DummyMacroDef(_Tag):
    """Parse global macro definitions."""

    def __init__(self, name: str, pattern_obj: re.Pattern) -> None:
        super().__init__(name, pattern_obj, str)

    def update_impl(self, spec_obj: "Spec", context: typing.Dict[str, typing.Any], match_obj: re.Match, line: str) -> typing.Any:
        context["line_processor"] = None
        warn("Unknown macro: " + line)
        return spec_obj, context


class _SectionStartMacrodef(_Tag):
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store')
    parser.add_argument('-n', action='store')
    parser.add_argument('content', nargs='*')
   
    def __init__(self, name: str) -> None:
        super().__init__(name, re.compile(r"^%("+name+")(?:\s+(.+))?$"), list)
    
    def line_processor(propName, context: typing.Dict[str, typing.Any], line: str) -> None:
        getattr(context["current_subpackage"], propName).append(line)

    def update_impl(self, spec_obj: "Spec", context: typing.Dict[str, typing.Any], match_obj: re.Match, line: str) -> typing.Any:
        macroName = match_obj.group(1)
        commandLine = match_obj.group(2)
        if commandLine:
            res, rest = self.__class__.parser.parse_known_args(commandLine.split(" "))
            if rest:
                raise ValueError(rest)
            spkg = context["current_subpackage"]
            pkgName = None
            if res.n:
                pkgName = res.n
            #elif not res.f:
            #    if len(res.content) != 1:
            #        raise ValueError()
            #    pkgName = "-".join((spec_obj.name, res.content[0]))

            if pkgName:
                spkg = context["current_subpackage"] = spec_obj.packages_dict[pkgName]
        else:
            res = None
            context["current_subpackage"] = spec_obj
 
        if res:
            prop = getattr(spkg, self.name)
            if res.f:
                try:
                    f = Path(res.f)
                    for l in f.splitlines():
                        l = l.strip()
                        prop.append(f)
                except:
                    warn("File ignored as nonexistent: " + res.f)
            for f in res.content:
                prop.append(f)
        else:
            context["line_processor"] = partial(self.__class__.line_processor, self.name)
        
        return spec_obj, context


class _InSectionMacroProp(_Tag):
    def __init__(self, name: str, pattern_obj: typing.Optional[re.Pattern] = None) -> None:
        if pattern_obj is None:
            pattern_obj = re.compile(r"^%("+name+")(?:\s+(.+))?$")
        super().__init__(name, pattern_obj, list)

    def update_impl(self, spec_obj: "Spec", context: typing.Dict[str, typing.Any], match_obj: re.Match, line: str) -> typing.Tuple["Spec", dict]:
        macroName = match_obj.group(1)
        commandLine = match_obj.group(2)
        spkg = context["current_subpackage"]
        prop = getattr(spkg, self.name)
        prop.append(commandLine)
        return spec_obj, context



class _List(_Tag):
    """Parse a tag that expands to a list."""

    def __init__(self, name: str, pattern_obj: re.Pattern) -> None:
        super().__init__(name, pattern_obj, list)

    def update_impl(self, spec_obj: "Spec", context: typing.Dict[str, typing.Any], match_obj: re.Match, line: str) -> typing.Tuple["Spec", dict]:
        context["line_processor"] = False
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

    def __init__(self, name: str, pattern_obj: re.Pattern) -> None:
        super().__init__(name, pattern_obj, list)

    def update_impl(self, spec_obj: "Spec", context: typing.Dict[str, typing.Any], match_obj: re.Match, line: str) -> typing.Tuple["Spec", dict]:
        context["line_processor"] = False
        source_name, value = match_obj.groups()
        dictionary = getattr(spec_obj, "{}_dict".format(self.name))
        dictionary[source_name] = value
        target_obj = _Tag.current_target(spec_obj, context)
        getattr(target_obj, self.name).append(value)
        return spec_obj, context

def elvis(*args):
    try:
        return next(filter(None, *args), None)
    except:
        pass

def dictElvis(prop: str, *args):
    for o in args:
        try:
            return getattr(o, prop)
        except:
            pass

_tags = [
    _NameValue("name", re.compile(r"^Name:\s*(\S+)")),
    _NameValue("version", re.compile(r"^Version:\s*(\S+)")),
    _NameValue("epoch", re.compile(r"^Epoch:\s*(\S+)")),
    _NameValue("release", re.compile(r"^Release:\s*(\S+)")),
    _NameValue("summary", re.compile(r"^Summary:\s*(.+)")),
    _NameValue("license", re.compile(r"^License:\s*(.+)")),
    _NameValue("group", re.compile(r"^Group:\s*(\S+)")),
    _NameValue("url", re.compile(r"^URL:\s*(\S+)")),
    _NameValue("buildroot", re.compile(r"^BuildRoot:\s*(\S+)")),
    _NameValue("buildarch", re.compile(r"^BuildArch:\s*(\S+)")),
    _ListAndDict("sources", re.compile(r"^(Source\d*):\s*(\S+)")),
    _ListAndDict("patches", re.compile(r"^(Patch\d*):\s*(\S+)")),
    _List("build_requires", re.compile(r"^BuildRequires:\s*(.+)")),
    _List("requires", re.compile(r"^Requires:\s*(.+)")),
    _List("conflicts", re.compile(r"^Conflicts:\s*(.+)")),
    _List("obsoletes", re.compile(r"^Obsoletes:\s*(.+)")),
    _List("provides", re.compile(r"^Provides:\s*(.+)")),
    _List("packages", re.compile(r"^%package\s+(\S+)")),
    
    _LocalMacroDef("define", re.compile(r"^%define\s+(\S+)\s+(\S+)")),
    _GlobalMacroDef("global", re.compile(r"^%global\s+(\S+)\s+(\S+)")),
    
    _SectionStartMacrodef("install"),
    _InSectionMacroProp("pre"),
    _InSectionMacroProp("post"),
    _InSectionMacroProp("postun"),
    _InSectionMacroProp("postun"),
    
    _SectionStartMacrodef("files"),
    _InSectionMacroProp("dir"),
    _InSectionMacroProp("exclude"),
    _InSectionMacroProp("doc"),
    _InSectionMacroProp("config", re.compile(r"^%(config)(?:\(noreplace\))?(?:\s*(.+))?$")),
    
    _SectionStartMacrodef("clean"),
    _SectionStartMacrodef("build"),
    _SectionStartMacrodef("prep"),
    _SectionStartMacrodef("description"),
    _SectionStartMacrodef("changelog"),

    
    _DummyMacroDef("dummy", re.compile(r"^%[a-z_]+\b.*$")),
]

_macro_pattern = re.compile(r"%{(\S+?)\}")


def _parse(spec_obj: "Spec", context: typing.Dict[str, typing.Any], line: str) -> typing.Any:
    actually_replaced = 1
    def line_replacer(m):
        nonlocal actually_replaced
        vn = m.group(1)
        if hasattr(spec_obj, vn):
            actually_replaced += 1
            return getattr(spec_obj, vn)
        else:
            return m.group(0)

    while actually_replaced>0:
        actually_replaced = 0
        line, _ = variableRx.subn(line_replacer, line)
    
    for tag in _tags:
        match = tag.test(line)
        if match:
            return tag.update(spec_obj, context, match, line)
    if context["line_processor"]:
        context["line_processor"](context, line)
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

    def __init__(self, name: str) -> None:
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

    def __init__(self, name: str) -> None:
        assert isinstance(name, str)

        for tag in _tags:
            if tag.attr_type is list:
                setattr(self, tag.name, tag.attr_type())

        self.name = name
        self.is_subpackage = False

    def __repr__(self) -> str:
        return "Package('{}')".format(self.name)


variableRx = re.compile("\%\{([a-zA-Z0-9_]+)\}")
InitializerDictT = typing.Optional[typing.Dict[str, typing.Any]]

class Spec:
    """Represents a single spec file.

    """

    def __init__(self, initial: InitializerDictT = None) -> None:
        for tag in _tags:
            if tag.attr_type is list:
                setattr(self, tag.name, tag.attr_type())
            else:
                setattr(self, tag.name, None)

        self.sources_dict = dict()
        self.patches_dict = dict()
        if initial is not None:
            self.__dict__.update(initial)
        

    @property
    def packages_dict(self) -> typing.Dict[str, Package]:
        """All packages in this RPM spec as a dictionary.

        You can access the individual packages by their package name, e.g.,

        git_spec.packages_dict['git-doc']

        """
        assert self.packages
        return dict(zip([package.name for package in self.packages], self.packages))

    @staticmethod
    def from_file(filename: str, initial: InitializerDictT = None) -> "Spec":
        """Creates a new Spec object from a given file.

        :param filename: The path to the spec file.
        :return: A new Spec object.
        """

        spec = Spec(initial)
        with open(filename, "r", encoding="utf-8") as f:
            parse_context = init_context(spec)
            for line in f:
                spec, parse_context = _parse(spec, parse_context, line)
        return spec

    @staticmethod
    def from_string(string: str, initial: InitializerDictT = None) -> "Spec":
        """Creates a new Spec object from a given string.

        :param string: The contents of a spec file.
        :return: A new Spec object.
        """

        spec = Spec(initial)

        parse_context = init_context(spec)
        for line in string.splitlines():
            spec, parse_context = _parse(spec, parse_context, line)
        return spec

def init_context(spec: Spec) -> typing.Dict[str, typing.Union[Spec, None]]:
    return {"current_subpackage": spec, "line_processor": None}


def replace_macros(string: str, spec: typing.Dict[str, typing.Any] = None) -> str:
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
            if _test_conditional(macro_name):  # ?
                if hasattr(spec, parts[0]):
                    if len(parts) == 2:
                        return parts[1]

                    return getattr(spec, parts[0], None)

                return ""
            else:  # !
                if not hasattr(spec, parts[0]):
                    if len(parts) == 2:
                        return parts[1]

                    return getattr(spec, parts[0], None)

                return ""

        if spec:
            value = getattr(spec, macro_name, None)
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
