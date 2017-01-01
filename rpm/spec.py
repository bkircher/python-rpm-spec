"""Python module for parsing RPM spec files.

RPMs are build from a package's sources along with a spec file. The spec file controls how the RPM
is built. This module allows you to parse spec files and gives you simple access to various bits of
information that is contained in the spec file.

Current status: This module does not parse everything of a spec file. Only the pieces I needed. So
there is probably still plenty of stuff missing. However, it should not be terribly complicated to
add support for the missing pieces.

"""

import re

__all__ = ['Spec', 'replace_macros']

_tags = {
    'name': (str, re.compile(r'^Name:\s*(\S+)')),
    'version': (str, re.compile(r'^Version:\s*(\S+)')),
    'epoch': (int, re.compile(r'^Epoch:\s*(\S+)')),
    'release': (str, re.compile(r'^Release:\s*(\S+)')),
    'summary': (str, re.compile(r'^Summary:\s*(.+)')),
    'license': (str, re.compile(r'^License:\s*(.+)')),
    'group': (str, re.compile(r'^Group:\s*(\S+)')),
    'url': (str, re.compile(r'^URL:\s*(\S+)')),
    'buildroot': (str, re.compile(r'^BuildRoot:\s*(\S+)')),
    'buildarch': (str, re.compile(r'^BuildArch:\s*(\S+)')),
    'sources': (list, re.compile(r'^Source\d*:\s*(\S+)')),
    'patches': (list, re.compile(r'^Patch\d*:\s*(\S+)')),
    'build_requires': (list, re.compile(r'^BuildRequires:\s*(.+)')),
    'requires': (list, re.compile(r'^Requires:\s*(.+)')),
}

_macro_pattern = re.compile(r'%\{(\S+?)\}')


def _parse(spec_obj, line):
    for name, value in _tags.items():
        attr_type, regex = value
        match = re.search(regex, line)
        if match:
            tag_value = match.group(1)
            if attr_type is list:
                if not hasattr(spec_obj, name):
                    setattr(spec_obj, name, list())
                getattr(spec_obj, name).append(tag_value)
            else:
                setattr(spec_obj, name, attr_type(tag_value))
    return spec_obj


class Spec:
    """Represents a single spec file.

    """

    @staticmethod
    def from_file(filename):
        """Creates a new Spec object from a given file.

        :param filename: The path to the spec file.
        :return: A new Spec object.
        """

        spec = Spec()
        with open(filename, 'r') as f:
            for line in f:
                spec = _parse(spec, line)
        return spec


def replace_macros(string, spec=None):
    """Replace all macros in given string with corresponding values.

    For example: a string '%{name}-%{version}.tar.gz' will be transformed to 'foo-2.0.tar.gz'.

    TODO: There is also `rpm --eval "%{macro}"` which could give us the expanded definition of a
    macro. Useful for macros that are global, e.g. %{_build_arch}.

    """
    if spec:
        assert isinstance(spec, Spec)

    def _macro_repl(match):
        attr_name = match.group(1)
        if spec:
            value = getattr(spec, attr_name, None)
            if value:
                return value
        return match.string[match.start():match.end()]

    return re.sub(_macro_pattern, _macro_repl, string)
