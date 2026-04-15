# taken from my Iphone pythonica dumper

# Android GEN of my Star wars Revnage
import os
import sys
import pkgutil
import platform

try:
    from importlib.metadata import distributions
except Exception:
    distributions = None

OUTPUT_NAME = "python_full_dump.txt"

def build_dump_text():
    parts = []
    def w(s=""):
        parts.append(s)
    w("="*60)
    w("ENVIRONMENT INFO")
    w("="*60)
    w(f"Python Executable: {sys.executable}")
    w(f"Python Version: {sys.version}")
    w(f"Platform: {platform.platform()}")
    w("")
    w("="*60)
    w("SYS.PATH")
    w("="*60)
    for p in sys.path:
        w(p)
    w("")
    w("="*60)
    w("PIP INSTALLED PACKAGES")
    w("="*60)
    if distributions is not None:
        try:
            pkgs = sorted((dist.metadata.get("Name", "UNKNOWN"), dist.version) for dist in distributions())
            for name, ver in pkgs:
                w(f"{name}=={ver}")
        except Exception as e:
            w(f"Failed to list installed packages: {e}")
    else:
        w("importlib.metadata.distributions not available")
    w("")
    w("="*60)
    w("BUILT-IN MODULES")
    w("="*60)
    for name in sorted(sys.builtin_module_names):
        w(name)
    w("")
    w("="*60)
    w("ALL IMPORTABLE MODULES (STDLIB + INSTALLED)")
    w("="*60)
    try:
        modules = sorted({m.name for m in pkgutil.iter_modules()})
        for m in modules:
            w(m)
    except Exception as e:
        w(f"Failed to list importable modules: {e}")
    return "\n".join(parts)

def same_folder_path(filename):
    try:
        base = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
    except NameError:
        base = os.getcwd()
    return os.path.join(base, filename)

def main():
    text = build_dump_text()
    out_path = same_folder_path(OUTPUT_NAME)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"Failed to write file: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Saved dump to: {out_path}")

if __name__ == "__main__":
    main()
