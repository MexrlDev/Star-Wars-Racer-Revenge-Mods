import sys
import os
import pkgutil
from importlib.metadata import distributions
import platform

OUTPUT_FILE = "python_full_dump.txt"

def write_header(f, title):
    f.write("\n" + "="*60 + "\n")
    f.write(title + "\n")
    f.write("="*60 + "\n\n")

def dump_environment(f):
    write_header(f, "ENVIRONMENT INFO")
    f.write(f"Python Executable: {sys.executable}\n")
    f.write(f"Python Version: {sys.version}\n")
    f.write(f"Platform: {platform.platform()}\n")

def dump_sys_path(f):
    write_header(f, "SYS.PATH")
    for path in sys.path:
        f.write(path + "\n")

def dump_installed_packages(f):
    write_header(f, "PIP INSTALLED PACKAGES")
    packages = sorted(
        (dist.metadata["Name"], dist.version)
        for dist in distributions()
    )
    for name, version in packages:
        f.write(f"{name}=={version}\n")

def dump_builtin_modules(f):
    write_header(f, "BUILT-IN MODULES")
    for name in sorted(sys.builtin_module_names):
        f.write(name + "\n")

def dump_all_modules(f):
    write_header(f, "ALL IMPORTABLE MODULES (STDLIB + INSTALLED)")
    modules = sorted({module.name for module in pkgutil.iter_modules()})
    for mod in modules:
        f.write(mod + "\n")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, OUTPUT_FILE)

    with open(output_path, "w", encoding="utf-8") as f:
        dump_environment(f)
        dump_sys_path(f)
        dump_installed_packages(f)
        dump_builtin_modules(f)
        dump_all_modules(f)

    print(f"Full dump saved to: {output_path}")

if __name__ == "__main__":
    main()
