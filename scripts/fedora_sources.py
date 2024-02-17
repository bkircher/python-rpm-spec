import os
import sys

from pyrpm.spec import Spec


# Spec files to skip because of known issues.
skipfiles = ()


def skip(filename: str) -> bool:
    if filename in skipfiles:
        return True

    for name in skipfiles:
        if filename.startswith(name):
            return True

    return False


if len(sys.argv) < 2:
    print("Error: missing argument")
    sys.exit(1)

rpmspecs = f"{sys.argv[1]}/rpm-specs/"

for _, _, filenames in os.walk(rpmspecs):
    for filename in filenames:
        if not skip(filename):
            print(filename)
            Spec.from_file(os.path.join(rpmspecs, filename))
