import os.path

from rpm.spec import Spec, replace_macros

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class TestSpecFileParser:
    def test_parse_perl_array_compare_spec(self):
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'perl-Array-Compare.spec'))
        assert isinstance(spec, Spec)

        assert 'perl-Array-Compare' == spec.name

        summary_info = {'Default': ['Perl extension for comparing arrays']}
        assert summary_info == spec.summary
        assert 1 == spec.epoch

        assert '1.16' == spec.version
        assert 'noarch' == spec.buildarch
        assert 2 == len(spec.build_requires)
        assert 'perl >= 1:5.6.0' == spec.build_requires[0]

    def test_parse_llvm_spec(self):
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'llvm.spec'))

        assert 'llvm' == spec.name
        assert '3.8.0' == spec.version

        assert 2 == len(spec.sources)
        assert 'http://llvm.org/releases/%{version}/%{name}-%{version}.src.tar.xz' == \
               spec.sources[0]
        assert 'llvm-config.h' == spec.sources[1]

        assert 1 == len(spec.patches)
        assert 'llvm-3.7.1-cmake-s390.patch' == spec.patches[0]


class TestReplaceMacro:
    def test_replace_macro_with_spec(self):
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'llvm.spec'))
        assert 'http://llvm.org/releases/3.8.0/llvm-3.8.0.src.tar.xz' == replace_macros(
            spec.sources[0], spec)
        assert 'llvm-config.h' == replace_macros(spec.sources[1], spec)

    def test_replace_without_spec(self):
        s = 'http://llvm.org/releases/%{version}/%{name}-%{version}.src.tar.xz'
        assert s == replace_macros(s, spec=None)

    def test_replace_unknown_macro(self):
        s = '%{foobar}'
        assert s == replace_macros(s, spec=None)

    def test_replace_macro_int_type_val(self):
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'perl-Array-Compare.spec'))
        s = '%{epoch}'
        print(replace_macros(s, spec))
        assert '1' == replace_macros(s, spec)
