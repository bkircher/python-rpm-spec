from pyrpm.spec import Spec

spec = Spec.from_file("llvm.spec")
print(spec.version)  # 3.8.0
print(spec.description)

for package in spec.packages:
    print(f'{package.name}: {package.summary if hasattr(package, "summary") else spec.summary}')
    print(package.description)
    print()


