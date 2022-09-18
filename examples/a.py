from pyrpm.spec import Spec, replace_macros

spec = Spec.from_file("llvm.spec")
print(spec.version)  # 3.8.0
print(spec.sources[0])  # http://llvm.org/releases/%{version}/%{name}-%{version}.src.tar.xz
print(replace_macros(spec.sources[0], spec))  # http://llvm.org/releases/3.8.0/llvm-3.8.0.src.tar.xz

for package in spec.packages:
    print(f'{package.name}: {package.summary if hasattr(package, "summary") else spec.summary}')

    # llvm: The Low Level Virtual Machine
    # llvm-devel: Libraries and header files for LLVM
    # llvm-doc: Documentation for LLVM
    # llvm-libs: LLVM shared libraries
    # llvm-static: LLVM static libraries
