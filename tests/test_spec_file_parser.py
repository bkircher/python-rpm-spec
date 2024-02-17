import re
import os.path

import pytest

import pyrpm.spec
from pyrpm.spec import Package, Requirement, Spec, replace_macros

TEST_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


# pylint: disable=protected-access


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class TestPackageClass:
    def test_repr_string(self) -> None:
        package = Package("foo")
        assert package.name == "foo"
        assert str(package) == "Package('foo')"

    def test_is_subpackage(self) -> None:
        package = Package("foo")
        assert package.is_subpackage is False


class TestRequirementClass:
    def test_repr_string(self) -> None:
        req = Requirement("foo")
        assert req.name == "foo"
        assert str(req) == "Requirement('foo')"

    def test_equal_to_string(self) -> None:
        req = Requirement("foo")
        assert req == "foo"

    def test_equal_to_string_with_version(self) -> None:
        req = Requirement("foo >= 0.1")
        assert req == "foo >= 0.1"

    def test_equal_to_other_requirement(self) -> None:
        req = Requirement("foo")
        assert req == Requirement("foo")

    def test_equal_to_other_requirement_with_version(self) -> None:
        req = Requirement("foo >= 0.1")
        assert req == Requirement("foo >= 0.1")


class TestSpecFileParser:
    def test_parse_perl_array_compare_spec(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "perl-Array-Compare.spec"))
        assert isinstance(spec, Spec)

        assert spec.name == "perl-Array-Compare"
        assert spec.summary == "Perl extension for comparing arrays"
        assert spec.epoch == "1"

        assert spec.version == "1.16"
        assert len(spec.build_requires) == 2
        assert spec.build_requires[0].line == "perl >= 1:5.6.0"

        assert spec.buildarch == "noarch"
        assert spec.excludearch == "alpha"
        assert spec.exclusivearch == "i386 x86_64"
        assert spec.buildarch_list == ["noarch"]
        assert spec.excludearch_list == ["alpha"]
        assert spec.exclusivearch_list == ["i386", "x86_64"]

    def test_parse_llvm_spec(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "llvm.spec"))

        assert spec.name == "llvm"
        assert spec.version == "3.8.0"

        assert len(spec.sources) == 2
        assert spec.sources[0] == "http://llvm.org/releases/%{version}/%{name}-%{version}.src.tar.xz"
        assert spec.sources[1] == "llvm-config.h"

        assert len(spec.patches) == 1
        assert spec.patches[0] == "llvm-3.7.1-cmake-s390.patch"

    def test_parse_only_base_package(self) -> None:
        # spec file does not contain %package directive
        spec = Spec.from_file(os.path.join(TEST_DATA, "perl-Array-Compare.spec"))
        assert len(spec.packages) == 1
        assert spec.packages[0].name == "perl-Array-Compare"
        assert not spec.packages[0].is_subpackage

    def test_parse_subpackages(self) -> None:
        # spec file contains four sub-packages and one base package
        spec = Spec.from_file(os.path.join(TEST_DATA, "llvm.spec"))
        assert len(spec.packages) == 5

        for package in spec.packages:
            assert isinstance(package, Package)
            assert package.name.startswith("llvm")

    def test_parse_subpackage_names(self) -> None:
        # spec file contains %package -n directive
        spec = Spec.from_file(os.path.join(TEST_DATA, "jsrdbg.spec"))
        assert len(spec.packages) == 3

        expected = ["jrdb", "jsrdbg", "jsrdbg-devel"]
        actual = [package.name for package in spec.packages]
        for name in expected:
            assert name in actual

    @pytest.mark.parametrize("element", ["BuildRequires", "Requires", "Conflicts", "Obsoletes", "Provides"])
    def test_end_of_line_comment_in_list(self, element):
        spec = Spec.from_string(
            f"""
{element}:  a
{element}:  b # some comment
{element}:  c # some comment
"""
        )
        assert getattr(spec, camel_to_snake(element)) == ["a", "b", "c"]

    def test_packages_dict_property(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "perl-Array-Compare.spec"))
        assert isinstance(spec.packages_dict, dict)
        assert len(spec.packages_dict) == len(spec.packages)

        spec = Spec.from_file(os.path.join(TEST_DATA, "llvm.spec"))
        assert isinstance(spec.packages_dict, dict)
        assert len(spec.packages_dict) == len(spec.packages)

    def test_sources_dict_property(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "llvm.spec"))
        assert len(spec.sources_dict) == len(spec.sources)
        assert spec.sources_dict["Source0"] is spec.sources[0]
        assert spec.sources_dict["Source100"] is spec.sources[1]

    def test_patches_dict_property(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "llvm.spec"))
        assert len(spec.patches_dict) == len(spec.patches)
        assert spec.patches_dict["Patch0"] is spec.patches[0]

    def test_subpackage_tags(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "jsrdbg.spec"))

        # Summary: tag
        assert spec.summary == "JavaScript Remote Debugger for SpiderMonkey"
        packages = spec.packages_dict
        assert packages["jsrdbg-devel"].summary == "Header files, libraries and development documentation for %{name}"
        assert packages["jrdb"].summary == "A command line debugger client for %{name}"

    def test_defines(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "attica-qt5.spec"))

        # Check if they exist
        for define in ("sonum", "_tar_path", "_libname", "rname"):
            assert hasattr(spec, define)

        # Check values
        assert spec.sonum == "5"
        assert spec.rname == "attica"
        assert spec._libname == "KF5Attica"
        assert spec._tar_path == "5.31"

    def test_replace_macro_that_is_tag_name(self) -> None:
        """Test that we are able to replace macros which are in the tag list.

        See issue https://github.com/bkircher/python-rpm-spec/issues/33.

        """
        spec = Spec.from_string(
            r"""
%global myversion 1.2.3
Version: %{myversion}
        """
        )
        assert replace_macros(spec.version, spec) == "1.2.3"

        spec = Spec.from_string(
            r"""
%global version 1.2.3
Version: %{version}
        """
        )
        assert replace_macros(spec.version, spec) == "1.2.3"

    def test_custom_conditional_macro(self) -> None:
        """Test that a user-defined conditional macro is being replaced."""
        spec = Spec.from_string(
            r"""
Name: foo
Version: 1
Release: 1%{?dist}
        """
        )
        spec.macros["dist"] = ".el8"
        assert replace_macros(f"{spec.name}-{spec.version}-{spec.release}.src.rpm", spec) == "foo-1-1.el8.src.rpm"

    def test_replace_macro_raises_with_max_attempts_reached(self) -> None:
        """Test that replace_macros accepts a max_attempts

        Make sure that replace_macros raises RuntimeError if max_attempts is reached.

        """
        spec = Spec.from_string(
            r"""
%global version 1
Version: %{version}
        """
        )
        with pytest.raises(RuntimeError):
            replace_macros(spec.version, spec, max_attempts=1)

    def test_requirement_parsing(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "attica-qt5.spec"))

        assert spec.build_requires[0].name == "cmake"
        assert spec.build_requires[0].version == "3.0"
        assert spec.build_requires[0].operator == ">="

    def test_subpackage_has_requires(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "git.spec"))

        core_package = spec.packages_dict["git-core"]
        assert len(core_package.requires) == 3

    def test_subpackage_has_build_requires(self) -> None:
        """Make sure that Requires:, BuildRequires:, and so on exist on
        sub-packages even though they might be empty.

        """
        spec = Spec.from_file(os.path.join(TEST_DATA, "git.spec"))

        core_package = spec.packages_dict["git-core"]
        assert not core_package.build_requires

    def test_multiline_context_from_file(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "foo.spec"))
        assert spec.description == os.linesep.join(["line 1", "", "line 2", "line 3", "", ""])
        assert spec.changelog == os.linesep.join(
            [
                "* Thu Jul  7 2022 First Last <name@example.com> - 1-2",
                "- blah blah blah.",
                "",
                "* Thu Jun 16 2022 First Last <name@example.com> - 1-1",
                "- blah blah blah.",
                "",
            ]
        )

    def test_multiline_context_from_string(self) -> None:
        spec = Spec.from_string(
            r"""
Name: foo
Version: 1
Release: 1

%description
line 1

line 2
line 3

%changelog
* Thu Jul  7 2022 First Last <name@example.com> - 1-2
- blah blah blah.

* Thu Jun 16 2022 First Last <name@example.com> - 1-1
- blah blah blah.
"""
        )
        assert spec.description == os.linesep.join(["line 1", "", "line 2", "line 3", "", ""])
        assert spec.changelog == os.linesep.join(
            [
                "* Thu Jul  7 2022 First Last <name@example.com> - 1-2",
                "- blah blah blah.",
                "",
                "* Thu Jun 16 2022 First Last <name@example.com> - 1-1",
                "- blah blah blah.",
                "",
            ]
        )


class TestSpecClass:
    def test_default_init(self) -> None:
        spec = Spec()
        assert spec.name is None
        assert spec.version is None
        assert spec.epoch is None
        assert spec.release is None
        assert spec.summary is None
        assert spec.license is None
        assert spec.group is None
        assert spec.url is None
        assert spec.buildroot is None
        assert spec.buildarch is None
        assert spec.sources == []
        assert spec.patches == []
        assert spec.build_requires == []
        assert spec.requires == []
        assert not spec.packages


class TestReplaceMacro:
    def test_replace_macro_without_spec_raises(self) -> None:
        """Make sure to assert that caller passes a spec file."""

        with pytest.raises(AssertionError):
            replace_macros("something something", spec=None)

    def test_replace_unknown_section(self) -> None:
        """Ensure that we can print warnings during parsing."""

        try:
            pyrpm.spec.warnings_enabled = True
            with pytest.warns(UserWarning):
                Spec.from_file(os.path.join(TEST_DATA, "perl-Array-Compare.spec"))
        finally:
            pyrpm.spec.warnings_enabled = False

    def test_replace_unknown_macro(self) -> None:
        """Ensure that string that do not have a definition in the spec file are left intact."""

        spec = Spec.from_file(os.path.join(TEST_DATA, "perl-Array-Compare.spec"))
        s = "%{foobar}"
        assert s == replace_macros(s, spec=spec)

    def test_replace_macro_int_type_val(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "perl-Array-Compare.spec"))
        result = replace_macros("%{epoch}", spec)
        assert isinstance(result, str)

    def test_replace_macro_twice(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "jsrdbg.spec"))
        # pylint: disable=line-too-long
        assert (
            replace_macros(spec.sources[0], spec)
            == "https://github.com/swojtasiak/jsrdbg/archive/26f9f2b27c04b4aec9cd67baaf9a0a206bbbd5c7.tar.gz#/jsrdbg-26f9f2b27c04b4aec9cd67baaf9a0a206bbbd5c7.tar.gz"
        )

    def test_replace_user_defined_macro(self) -> None:
        spec = Spec.from_string(
            """
Name:           foo
Version:        2
%define var   bar
"""
        )
        s = "%{name}/%{version}/%{var}"
        assert replace_macros(s, spec) == "foo/2/bar"

    def test_replace_macro_without_braces(self) -> None:
        spec = Spec.from_string(
            """
%define var bar
"""
        )
        assert replace_macros("foo-%var", spec) == "foo-bar"

    def test_replace_macro_with_negative_conditional(self) -> None:
        spec = Spec.from_file(os.path.join(TEST_DATA, "git.spec"))

        assert (
            replace_macros(
                "https://www.kernel.org/pub/software/scm/git/%{?rcrev:testing/}%{name}-%{version}%{?rcrev}.tar.xz",
                spec,
            )
            == "https://www.kernel.org/pub/software/scm/git/git-2.15.1.tar.xz"
        )

    def test_replace_macro_with_positive_conditional(self) -> None:
        spec = Spec.from_string(
            """
Name:           git
Version:        2.15.1
%define rcrev   .rc0
        """
        )

        assert (
            replace_macros(
                "https://www.kernel.org/pub/software/scm/git/%{?rcrev:testing/}%{name}-%{version}%{?rcrev}.tar.xz",
                spec,
            )
            == "https://www.kernel.org/pub/software/scm/git/testing/git-2.15.1.rc0.tar.xz"
        )

    def test_replace_macro_with_leading_exclamation_point(self) -> None:
        spec = Spec.from_string(
            """
Name:           git
Version:        2.15.1
        """
        )

        assert (
            replace_macros(
                "https://www.kernel.org/pub/software/scm/git/%{!stable:testing/}%{name}-%{version}.tar.xz",
                spec,
            )
            == "https://www.kernel.org/pub/software/scm/git/testing/git-2.15.1.tar.xz"
        )
