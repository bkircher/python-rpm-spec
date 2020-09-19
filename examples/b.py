from pyrpm.spec import Spec

spec = Spec.from_file("llvm.spec")

# Access sources and patches via name
for k, v in spec.sources_dict.items():
    print(f"{k} → {v}")

# Source0 → http://llvm.org/releases/%{version}/%{name}-%{version}.src.tar.xz
# Source100 → llvm-config.h

# Or as a list with indices and so on
for source in spec.sources:
    print(source)

# http://llvm.org/releases/%{version}/%{name}-%{version}.src.tar.xz
# llvm-config.h
