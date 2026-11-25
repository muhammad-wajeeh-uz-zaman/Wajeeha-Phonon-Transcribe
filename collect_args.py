"""Prints PyInstaller --collect-all flags for the installed fermion-research package.
(Used by build.bat so we don't have to guess the package's module names.)"""
import sys
import importlib.metadata as m

files = m.files("fermion-research") or []
pkgs = sorted({f.parts[0] for f in files
               if len(f.parts) > 1 and f.suffix == ".py"
               and not f.parts[0].endswith((".dist-info", ".data"))})
eps = [e.name for e in m.entry_points(group="console_scripts")
       if e.dist and e.dist.name.replace("_", "-").lower() == "fermion-research"]
print("fermion-research packages:", pkgs, "| commands:", eps, file=sys.stderr)
print(" ".join(f"--collect-all {p}" for p in pkgs))
