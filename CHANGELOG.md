# Changelog

## 0.13 (2022-11-01)

* Fix parsing of BuildRequires:, Requires:, Conflicts:, Obsoletes:, Provides: with comments at end of line. Thanks [@SuoXC](https://github.com/SuoXC).
* Add CI for Python 3.11.

## 0.12 (2022-07-13)

* Fix %description and %changelog with multi-line strings [#46](https://github.com/bkircher/python-rpm-spec/issues/46). Thanks [@tagoh](https://github.com/tagoh).

## 0.11 (2021-08-05)

Changes:

* Add type annotations for tools like mypy, your IDE, and your brain. Thanks [@KOLANICH](https://github.com/KOLANICH).
* `replace_macros()` function now always expects a Spec instance as second argument. Does not make much sense without.
* Add support for parsing %description and %changelog (see PR [#42](https://github.com/bkircher/python-rpm-spec/pull/42)). Thanks [@BrunoVernay](https://github.com/BrunoVernay).
* Add support for ExcludeArch and ExclusiveArch ([#45](https://github.com/bkircher/python-rpm-spec/pull/45)). Thanks [@tonsh](https://github.com/tonsh).
* Add `warnings_enabled` knob to issue [warnings](https://docs.python.org/3/library/warnings.html#module-warnings) of type `UserWarning` during spec file parsing.

## 0.10 (2020-09-19)

Changes:

* Ignore spaces before ':' separator (see PR [#32][https://github.com/bkircher/python-rpm-spec/pull/32])
* Fix behavior of replace_macro function when macro is a tag, too (see issue [#33](https://github.com/bkircher/python-rpm-spec/issues/33)).

## 0.9 (2020-05-02)

Changes:

* Ignore case when parsing directives

## 0.8 (2018-09-18)

New Features:

* Enable parsing versions in `BuildRequires:` and `Requires:`
* Add support for conditional macros, e.g. `%{?test_macro:expression}`
* Use flit for packaging

## 0.7 (2017-08-10)

New Features:

* Add `Spec.sources_dict` and `Spec.patches_dict`
