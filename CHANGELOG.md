# Changelog

## 0.9 (202-05-02)

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
