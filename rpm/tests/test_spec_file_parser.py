import unittest
from rpm.spec import Spec, replace_macros


class TestSpecFileParser(unittest.TestCase):
    def test_parse_perl_array_compare_spec(self):
        spec = Spec.from_file('perl-Array-Compare.spec')
        self.assertIsInstance(spec, Spec)

        self.assertEqual('perl-Array-Compare', spec.name)
        self.assertEqual('Perl extension for comparing arrays', spec.summary)
        self.assertEqual(1, spec.epoch)

        self.assertEqual('1.16', spec.version)
        self.assertEqual('noarch', spec.buildarch)
        self.assertEqual(2, len(spec.build_requires))
        self.assertEqual('perl >= 1:5.6.0', spec.build_requires[0])

    def test_parse_llvm_spec(self):
        spec = Spec.from_file('llvm.spec')

        self.assertEqual('llvm', spec.name)
        self.assertEqual('3.8.0', spec.version)

        self.assertEqual(2, len(spec.sources))
        self.assertEqual(
            'http://llvm.org/releases/%{version}/%{name}-%{version}.src.tar.xz',
            spec.sources[0])
        self.assertEqual(
            'llvm-config.h',
            spec.sources[1])

        self.assertEqual(1, len(spec.patches))
        self.assertEqual('llvm-3.7.1-cmake-s390.patch', spec.patches[0])


class TestReplaceMacro(unittest.TestCase):
    def test_replace_macro_with_spec(self):
        spec = Spec.from_file('llvm.spec')
        self.assertEqual(
            'http://llvm.org/releases/3.8.0/llvm-3.8.0.src.tar.xz',
            replace_macros(spec.sources[0], spec))
        self.assertEqual(
            'llvm-config.h',
            replace_macros(spec.sources[1], spec))

    def test_replace_without_spec(self):
        s = 'http://llvm.org/releases/%{version}/%{name}-%{version}.src.tar.xz'
        self.assertEqual(s, replace_macros(s, spec=None))

    def test_replace_unknown_macro(self):
        s = '%{foobar}'
        self.assertEqual(s, replace_macros(s, spec=None))


if __name__ == '__main__':
    unittest.main()
