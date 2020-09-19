# Changelog

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
