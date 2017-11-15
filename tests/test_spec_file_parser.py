import os.path

from pyrpm.spec import Package, Spec, replace_macros

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class TestPackageClass:
    def test_repr_string(self):
        package = Package('foo')
        assert package.name == 'foo'
        assert str(package) == "Package('foo')"

    def test_is_subpackage(self):
        package = Package('foo')
        assert package.is_subpackage is False


class TestSpecFileParser:
    def test_parse_perl_array_compare_spec(self):
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'perl-Array-Compare.spec'))
        assert isinstance(spec, Spec)

        assert 'perl-Array-Compare' == spec.name
        assert 'Perl extension for comparing arrays' == spec.summary
        assert 1 == spec.epoch

        assert '1.16' == spec.version
        assert 'noarch' == spec.buildarch
        assert 2 == len(spec.build_requires)
        assert 'perl >= 1:5.6.0' == spec.build_requires[0].line

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

    def test_parse_only_base_package(self):
        # spec file does not contain %package directive
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'perl-Array-Compare.spec'))
        assert len(spec.packages) == 1
        assert spec.packages[0].name == 'perl-Array-Compare'
        assert not spec.packages[0].is_subpackage

    def test_parse_subpackages(self):
        # spec file contains four subpackages and one base package
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'llvm.spec'))
        assert len(spec.packages) == 5

        for package in spec.packages:
            assert isinstance(package, Package)
            assert package.name.startswith('llvm')

    def test_parse_subpackage_names(self):
        # spec file contains %package -n directive
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'jsrdbg.spec'))
        assert len(spec.packages) == 3

        expected = ['jrdb', 'jsrdbg', 'jsrdbg-devel']
        actual = [package.name for package in spec.packages]
        for name in expected:
            assert name in actual

    def test_packages_dict_property(self):
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'perl-Array-Compare.spec'))
        assert isinstance(spec.packages_dict, dict)
        assert len(spec.packages_dict) == len(spec.packages)

        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'llvm.spec'))
        assert isinstance(spec.packages_dict, dict)
        assert len(spec.packages_dict) == len(spec.packages)

    def test_sources_dict_property(self):
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'llvm.spec'))
        assert len(spec.sources_dict) == len(spec.sources)
        assert spec.sources_dict['Source0'] is spec.sources[0]
        assert spec.sources_dict['Source100'] is spec.sources[1]

    def test_patches_dict_property(self):
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'llvm.spec'))
        assert len(spec.patches_dict) == len(spec.patches)
        assert spec.patches_dict['Patch0'] is spec.patches[0]

    def test_subpackage_tags(self):
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'jsrdbg.spec'))

        # Summary: tag
        assert spec.summary == 'JavaScript Remote Debugger for SpiderMonkey'
        packages = spec.packages_dict
        assert packages['jsrdbg-devel'].summary == \
            'Header files, libraries and development documentation for %{name}'
        assert packages['jrdb'].summary == 'A command line debugger client for %{name}'

    def test_defines(self):
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'attica-qt5.spec'))

        # Check if they exist
        for define in ("sonum", "_tar_path", "_libname", "rname"):
            assert hasattr(spec, define)

        # Check values
        assert spec.sonum == "5"
        assert spec.rname == "attica"
        assert spec._libname == "KF5Attica"
        assert spec._tar_path == "5.31"


class TestSpecClass:

    def test_default_init(self):
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
        assert spec.packages == []


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
        result = replace_macros('%{epoch}', spec)
        assert isinstance(result, str)

    def test_replace_macro_twice(self):
        spec = Spec.from_file(os.path.join(CURRENT_DIR, 'jsrdbg.spec'))
        assert 'https://github.com/swojtasiak/jsrdbg/archive/26f9f2b27c04b4aec9cd67baaf9a0a206bbbd5c7.tar.gz#/jsrdbg-26f9f2b27c04b4aec9cd67baaf9a0a206bbbd5c7.tar.gz' \
                == replace_macros(spec.sources[0], spec)
