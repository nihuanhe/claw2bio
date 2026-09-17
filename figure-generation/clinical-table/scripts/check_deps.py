#!/usr/bin/env python3
# check_deps.py - pre-run dependency check for the clinical-table skill.
# Run this FIRST (README quick-start step 1):  python scripts/check_deps.py
# Covers the generic engine (clinical_table.py). The R-pipeline helper
# make_table9_sequencing_quality.py is Python stdlib only - nothing to check.
# Exit code: 0 = ready, 1 = missing packages.

import importlib.metadata as md
import sys

REQUIRED = ["pandas", "numpy", "scipy", "statsmodels"]


def main() -> int:
    print(f"Python {sys.version.split()[0]}",
          "- OK for the bundled wheels (cp313, win_amd64)"
          if sys.version_info[:2] == (3, 13)
          else "- NOTE: bundled wheels target Python 3.13; use the online install")
    missing = []
    for name in REQUIRED:
        try:
            print(f"OK       {name} {md.version(name)}")
        except md.PackageNotFoundError:
            print(f"MISSING  {name}")
            missing.append(name)
    print()
    if not missing:
        print("ALL OK - the clinical-table skill is ready to run.")
        return 0
    print(f"{len(missing)} package(s) missing. Install with ONE of:")
    print("  ONLINE : pip install " + " ".join(REQUIRED))
    print("  OFFLINE: see README 'Offline install (Windows)'")
    print("           (bundled wheels: cos-staging/clinical-table/deps/python/)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
