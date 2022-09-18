from pyrpm.spec import Spec

spec = Spec.from_file("llvm.spec")
print(spec.name)
print(spec.description)

for package in spec.packages:
    print(f'{package.name}: {package.summary if hasattr(package, "summary") else spec.summary}')
    print(package.description)
    print()

print(spec.changelog)


# llvm
# LLVM is a compiler infrastructure designed for compile-time, link-time,
# runtime, and idle-time optimization of programs from arbitrary programming
# languages. The compiler infrastructure includes mirror sets of programming
# tools as well as libraries with equivalent functionality.
#
#
# llvm: The Low Level Virtual Machine
# None
#
# llvm-devel: Libraries and header files for LLVM
# This package contains library and header files needed to develop new native
# programs that use the LLVM infrastructure.
#
#
#
# llvm-doc: Documentation for LLVM
# Documentation for the LLVM compiler infrastructure.
#
#
#
# llvm-libs: LLVM shared libraries
# Shared libraries for the LLVM compiler infrastructure.
#
#
#
# llvm-static: LLVM static libraries
# Static libraries for the LLVM compiler infrastructure.
#
#
#
# * Thu Mar 10 2016 Dave Airlie <airlied@redhat.com> 3.8.0-1
# - llvm 3.8.0 release
# ...
# * Tue Oct 06 2015 Jan Vcelak <jvcelak@fedoraproject.org> 3.7.0-100
# - initial version using cmake build system
