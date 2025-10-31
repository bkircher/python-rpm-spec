"""Python module for parsing RPM spec files.

This module allows to parse RPM spec files and gives simple access to various bits of information contained in the spec file.

"""

from __future__ import annotations

import os
import re
from warnings import warn
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])

try:
    from typing import override  # type: ignore[attr-defined]
except ImportError:

    def override(func: F, /) -> F:
        return func


__all__ = ["Spec", "replace_macros", "Package", "warnings_enabled"]


# Set this to True if you want the library to issue warnings during parsing.
warnings_enabled: bool = False


class _Tag(metaclass=ABCMeta):
    def __init__(self, name: str, pattern_obj: re.Pattern[str], attr_type: type[Any]) -> None:
        self.name = name
        self.pattern_obj = pattern_obj
        self.attr_type = attr_type

    def test(self, line: str) -> re.Match[str] | None:
        return re.search(self.pattern_obj, line)

    def update(self, spec_obj: Spec, context: dict[str, Any], match_obj: re.Match[str], line: str) -> Any:
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
    def update_impl(
        self, spec_obj: Spec, context: dict[str, Any], match_obj: re.Match[str], line: str
    ) -> tuple[Spec, dict[str, Any]]:
        pass

    @staticmethod
    def current_target(spec_obj: Spec, context: dict[str, Any]) -> Spec | Package:
        target_obj = spec_obj
        if context["current_subpackage"] is not None:
            target_obj = context["current_subpackage"]
        return target_obj


class _NameValue(_Tag):
    """Parse a simple name → value tag."""

    def __init__(self, name: str, pattern_obj: re.Pattern[str], attr_type: type[Any] | None = None) -> None:
        super().__init__(name, pattern_obj, cast(type[Any], attr_type if attr_type else str))

    def update_impl(
        self, spec_obj: Spec, context: dict[str, Any], match_obj: re.Match[str], line: str
    ) -> tuple[Spec, dict[str, Any]]:
        if self.name == "changelog":
            context["current_subpackage"] = None

        target_obj = _Tag.current_target(spec_obj, context)
        value = match_obj.group(1)

        # Sub-packages
        if self.name == "name":
            spec_obj.packages = []
            spec_obj.packages.append(Package(value))

        if self.name in ["description", "changelog"]:
            context["multiline"] = self.name
        else:
            setattr(target_obj, self.name, self.attr_type(value))

        return spec_obj, context


class _SetterMacroDef(_Tag):
    """Parse global macro definitions."""

    def __init__(self, name: str, pattern_obj: re.Pattern[str]) -> None:
        super().__init__(name, pattern_obj, str)

    @abstractmethod
    def get_namespace(self, spec_obj: Spec, context: dict[str, Any]) -> Spec:
        raise NotImplementedError()

    def update_impl(
        self, spec_obj: Spec, context: dict[str, Any], match_obj: re.Match[str], line: str
    ) -> tuple[Spec, dict[str, Any]]:
        name, value = match_obj.groups()
        setattr(self.get_namespace(spec_obj, context), name, str(value))
        return spec_obj, context


class _GlobalMacroDef(_SetterMacroDef):
    """Parse global macro definitions."""

    def get_namespace(self, spec_obj: Spec, context: dict[str, Any]) -> Spec:
        return spec_obj


class _LocalMacroDef(_SetterMacroDef):
    """Parse define macro definitions."""

    def get_namespace(self, spec_obj: Spec, context: dict[str, Any]) -> Spec:
        return context["current_subpackage"]


class _MacroDef(_Tag):
    """Parse global macro definitions."""

    def __init__(self, name: str, pattern_obj: re.Pattern[str]) -> None:
        super().__init__(name, pattern_obj, str)

    def update_impl(
        self, spec_obj: Spec, context: dict[str, Any], match_obj: re.Match[str], line: str
    ) -> tuple[Spec, dict[str, Any]]:
        name, value = match_obj.groups()
        raw_value = str(value)
        stored_value = raw_value
        if _macro_references_itself(raw_value, name):
            try:
                stored_value = replace_macros(raw_value, spec_obj)
            except RuntimeError:
                stored_value = raw_value
        spec_obj.macros[name] = stored_value
        if name not in _tag_names:
            # Also make available as attribute of spec object
            setattr(spec_obj, name, stored_value)
        return spec_obj, context


def _macro_references_itself(raw_value: str, macro_name: str) -> bool:
    """Check if a macro definition references itself."""
    brace_pattern = rf"(?<!%)%{{{re.escape(macro_name)}}}"
    bare_pattern = rf"(?<!%)%{re.escape(macro_name)}\b"
    return bool(re.search(brace_pattern, raw_value) or re.search(bare_pattern, raw_value))


class _List(_Tag):
    """Parse a tag that expands to a list."""

    def __init__(self, name: str, pattern_obj: re.Pattern[str]) -> None:
        super().__init__(name, pattern_obj, list)

    def update_impl(
        self, spec_obj: Spec, context: dict[str, Any], match_obj: re.Match[str], line: str
    ) -> tuple[Spec, dict[str, Any]]:
        target_obj = _Tag.current_target(spec_obj, context)

        if not hasattr(target_obj, self.name):
            setattr(target_obj, self.name, [])

        value = match_obj.group(1)
        if self.name == "packages":
            if value == "-n":
                subpackage_name = re.split(r"\s+", line)[-1].rstrip()
            else:
                subpackage_name = f"{spec_obj.name}-{value}"
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
            # Remove comments on same line
            value = value.split("#", 2)[0].rstrip()

            # It's also legal to do:
            #   Requires: a b c
            #   Requires: b >= 3.1
            #   Requires: a, b >= 3.1, c

            # 1. Tokenize
            tokens = [val for val in re.split("[\t\n, ]", value) if val]
            values: list[str] = []

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

    def __init__(self, name: str, pattern_obj: re.Pattern[str]) -> None:
        super().__init__(name, pattern_obj, list)

    def update_impl(
        self, spec_obj: Spec, context: dict[str, Any], match_obj: re.Match[str], line: str
    ) -> tuple[Spec, dict[str, Any]]:
        source_name, value = match_obj.groups()
        dictionary = getattr(spec_obj, f"{self.name}_dict")
        dictionary[source_name] = value
        target_obj = _Tag.current_target(spec_obj, context)
        # If we are in a subpackage, add sources and patches to the subpackage dicts as well
        if hasattr(target_obj, "is_subpackage") and target_obj.is_subpackage:
            dictionary = getattr(target_obj, f"{self.name}_dict")
            dictionary[source_name] = value
            getattr(target_obj, self.name).append(value)
        getattr(spec_obj, self.name).append(value)
        return spec_obj, context


class _SplitValue(_NameValue):
    """Parse a (name->value) tag, and at the same time split the tag to a list."""

    def __init__(self, name: str, pattern_obj: re.Pattern[str], sep: str | None = None) -> None:
        super().__init__(name, pattern_obj)
        self.name_list = f"{name}_list"
        self.sep = sep

    def update_impl(
        self, spec_obj: Spec, context: dict[str, Any], match_obj: re.Match[str], line: str
    ) -> tuple[Spec, dict[str, Any]]:
        super().update_impl(spec_obj, context, match_obj, line)

        target_obj = _Tag.current_target(spec_obj, context)
        value: str = getattr(target_obj, self.name)
        values = value.split(self.sep)
        setattr(target_obj, self.name_list, values)

        return spec_obj, context


def re_tag_compile(tag: str) -> re.Pattern[str]:
    return re.compile(tag, re.IGNORECASE)


class _DummyMacroDef(_Tag):
    """Parse global macro definitions."""

    def __init__(self, name: str, pattern_obj: re.Pattern[str]) -> None:
        super().__init__(name, pattern_obj, str)

    def update_impl(
        self, spec_obj: Spec, context: dict[str, Any], match_obj: re.Match[str], line: str
    ) -> tuple[Spec, dict[str, Any]]:
        del match_obj
        context["line_processor"] = None
        if warnings_enabled:
            warn("Unknown macro: " + line)
        return spec_obj, context


_tags = [
    _NameValue("name", re_tag_compile(r"^Name\s*:\s*(\S+)")),
    _NameValue("version", re_tag_compile(r"^Version\s*:\s*(\S+)")),
    _NameValue("epoch", re_tag_compile(r"^Epoch\s*:\s*(\S+)")),
    _NameValue("release", re_tag_compile(r"^Release\s*:\s*(\S+)")),
    _NameValue("summary", re_tag_compile(r"^Summary\s*:\s*(.+)")),
    _NameValue("description", re_tag_compile(r"^%description\s*(\S*)")),
    _NameValue("changelog", re_tag_compile(r"^%changelog\s*(\S*)")),
    _NameValue("license", re_tag_compile(r"^License\s*:\s*(.+)")),
    _NameValue("group", re_tag_compile(r"^Group\s*:\s*(.+)")),
    _NameValue("url", re_tag_compile(r"^URL\s*:\s*(\S+)")),
    _NameValue("buildroot", re_tag_compile(r"^BuildRoot\s*:\s*(\S+)")),
    _SplitValue("buildarch", re_tag_compile(r"^BuildArch\s*:\s*(\S+)")),
    _SplitValue("excludearch", re_tag_compile(r"^ExcludeArch\s*:\s*(.+)")),
    _SplitValue("exclusivearch", re_tag_compile(r"^ExclusiveArch\s*:\s*(.+)")),
    _ListAndDict("sources", re_tag_compile(r"^(Source\d*\s*):\s*(.+)")),
    _ListAndDict("patches", re_tag_compile(r"^(Patch\d*\s*):\s*(\S+)")),
    _List("build_requires", re_tag_compile(r"^BuildRequires\s*:\s*(.+)")),
    _List("requires", re_tag_compile(r"^Requires\s*:\s*(.+)")),
    _List("conflicts", re_tag_compile(r"^Conflicts\s*:\s*(.+)")),
    _List("obsoletes", re_tag_compile(r"^Obsoletes\s*:\s*(.+)")),
    _List("provides", re_tag_compile(r"^Provides\s*:\s*(.+)")),
    _List("packages", re_tag_compile(r"^%package\s+(\S+)")),
    _MacroDef("define", re_tag_compile(r"^%define\s+(\S+)\s+(\S+)")),
    _MacroDef("global", re_tag_compile(r"^%global\s+(\S+)\s+(\S+)")),
    _DummyMacroDef("dummy", re_tag_compile(r"^%[a-z_]+\b.*$")),
]

_tag_names = [tag.name for tag in _tags]

_macro_pattern = re.compile(r"%{(\S+?)\}|%(\w+?)\b")


def _parse(spec_obj: Spec, context: dict[str, Any], line: str) -> Any:
    for tag in _tags:
        match = tag.test(line)
        if match:
            if "multiline" in context:
                context.pop("multiline", None)
            return tag.update(spec_obj, context, match, line)
    if "multiline" in context:
        target_obj = _Tag.current_target(spec_obj, context)
        previous_txt = getattr(target_obj, context["multiline"], "")
        if previous_txt is None:
            previous_txt = ""
        setattr(target_obj, context["multiline"], str(previous_txt) + line + os.linesep)

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
        self.name: str
        self.operator: str | None
        self.version: str | None
        match = Requirement.expr.match(name)
        if match:
            self.name = match.group(1)
            self.operator = match.group(2)
            self.version = match.group(3)
        else:
            self.name = name
            self.operator = None
            self.version = None

    @override
    def __eq__(self, o: object) -> bool:
        if isinstance(o, str):
            return self.line == o
        if isinstance(o, Requirement):
            return self.name == o.name and self.operator == o.operator and self.version == o.version
        return False

    @override
    def __repr__(self) -> str:
        return f"Requirement('{self.line}')"


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
            if tag.attr_type is list and tag.name in [
                "build_requires",
                "requires",
                "conflicts",
                "obsoletes",
                "provides",
                "sources",
                "patches",
            ]:
                setattr(self, tag.name, tag.attr_type())
            elif tag.name in [
                "description",
            ]:
                setattr(self, tag.name, None)

        self.sources_dict: dict[str, str] = {}
        self.patches_dict: dict[str, str] = {}
        self.name = name
        self.is_subpackage = False

    @override
    def __repr__(self) -> str:
        return f"Package('{self.name}')"


class Spec:
    """Represents a single spec file."""

    def __init__(self) -> None:
        for tag in _tags:
            if tag.attr_type is list:
                setattr(self, tag.name, tag.attr_type())
            else:
                setattr(self, tag.name, None)

        self.sources_dict: dict[str, str] = {}
        self.patches_dict: dict[str, str] = {}
        self.macros: dict[str, str] = {"nil": ""}

        self.name: str | None
        self.packages: list[Package] = []

    @property
    def packages_dict(self) -> dict[str, Package]:
        """All packages in this RPM spec as a dictionary.

        You can access the individual packages by their package name, e.g.,

        git_spec.packages_dict['git-doc']

        """
        assert self.packages
        return dict(zip([package.name for package in self.packages], self.packages))

    @classmethod
    def from_file(cls, filename: str) -> Spec:
        """Creates a new Spec object from a given file.

        :param filename: The path to the spec file.
        :return: A new Spec object.
        """

        spec = cls()
        with open(filename, "r", encoding="utf-8") as f:
            parse_context = {"current_subpackage": None}
            for line in f:
                spec, parse_context = _parse(spec, parse_context, line.rstrip())
        return spec

    @classmethod
    def from_string(cls, string: str) -> Spec:
        """Creates a new Spec object from a given string.

        :param string: The contents of a spec file.
        :return: A new Spec object.
        """

        spec = cls()
        parse_context = {"current_subpackage": None}
        for line in string.splitlines():
            spec, parse_context = _parse(spec, parse_context, line)
        return spec


def replace_macros(string: str, spec: Spec, max_attempts: int = 1000) -> str:
    """Replace all macros in given string with corresponding values.

    Note: If macros are not defined in the spec file, this won't try to
    expand them.

    For example, a string '%{name}-%{version}.tar.gz' will be transformed to 'foo-2.0.tar.gz'.

    :param string A string containing macros that you want to be replaced.
    :param spec A Spec object. Definitions in that spec file will be used to replace macros.
    :param max_attempts If reached, raises a RuntimeError.

    :return A string where all macros in given input are substituted as good as possible.

    """
    assert isinstance(spec, Spec)

    def get_first_non_none_value(values: tuple[Any, ...]) -> Any:
        return next((v for v in values if v is not None), None)

    def is_conditional_macro(macro: str) -> bool:
        return macro.startswith(("?", "!"))

    def is_optional_macro(macro: str) -> bool:
        return macro.startswith("?")

    def is_negation_macro(macro: str) -> bool:
        return macro.startswith("!")

    def get_replacement_string(match: re.Match[str]) -> str:
        # pylint: disable=too-many-return-statements
        groups = match.groups()
        macro_name: str = get_first_non_none_value(groups)
        assert macro_name, "Expected a non None value"
        if is_conditional_macro(macro_name) and spec:
            parts = macro_name[1:].split(sep=":", maxsplit=1)
            assert parts, "Expected a ':' in macro name'"
            macro = parts[0]
            if is_optional_macro(macro_name):
                if hasattr(spec, macro) or macro in spec.macros:
                    if len(parts) == 2:
                        return parts[1]

                    if macro in spec.macros:
                        return spec.macros[macro]

                    if hasattr(spec, macro):
                        return getattr(spec, macro)

                    assert False, "Unreachable"

                return ""

            if is_negation_macro(macro_name):
                if len(parts) == 2:
                    return parts[1]

                return spec.macros.get(macro, getattr(spec, macro, ""))

        if spec:
            value = spec.macros.get(macro_name, getattr(spec, macro_name, None))
            if value is not None:
                return str(value)

        return match.string[match.start() : match.end()]

    attempt = 0
    ret = ""
    while attempt < max_attempts:
        attempt += 1
        ret = re.sub(_macro_pattern, get_replacement_string, string)
        if ret != string:
            string = ret
            continue
        return ret

    raise RuntimeError("max_attempts reached. Aborting")
