from pyrpm.spec import Spec

spec = Spec.from_file("attica-qt5.spec")

# Access sources and patches via name
for br in spec.build_requires:
    print(f"{br.name} {br.operator} {br.version}" if br.version else f"{br.name}")

# cmake >= 3.0
# extra-cmake-modules >= %{_tar_path}
# fdupes
# kf5-filesystem
# pkg-config
# cmake(Qt5Core) >= 5.6.0
# cmake(Qt5Network) >= 5.6.0
