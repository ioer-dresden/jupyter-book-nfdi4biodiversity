#!/usr/bin/env bash
#  Quiet, root‑warning‑free Python package installer
#  (shows one line per package – already installed / installed)

set -euo pipefail                     # fail fast, treat unset vars as errors

# 1  Suppress the “Running pip as the 'root' user …” warning
export PIP_ROOT_USER_ACTION=ignore

# 1  Optional mapping for packages whose *distribution* name differs
#     from the name you type on the command line.
declare -A DIST_NAME_MAP=(
    [dotenv]="python-dotenv"   # `import dotenv` → PyPI name `python-dotenv`
    # add more overrides here if you discover them
)

# 3  Helper: ask the same interpreter ($PYTHON_BIN) for a version
_get_version() {
    # $1 = package name that you typed on the command line (e.g. "dotenv")
    local pkg="$1"
    local dist_name="${DIST_NAME_MAP[$pkg]:-$pkg}"   # use map if present

    # Run a one‑liner with the interpreter you gave to the script.
    "$PYTHON_BIN" - <<PY
import importlib.metadata as meta
import sys

dist = "${dist_name}"
try:
    # First try the PEP‑621/PEP‑566 distribution metadata
    print(meta.version(dist))
except meta.PackageNotFoundError:
    # Fallback: try to import the module and read its __version__ attr
    try:
        mod = __import("${pkg//-/_}")
        print(getattr(mod, "__version__", "unknown"))
    except Exception:
        print("unknown")
except Exception as e:
    # Any unexpected error – still print something so the script keeps going
    print("unknown")
PY
}

# 4  Main loop
PYTHON_BIN="$1"
shift                     # now $@ holds the list of packages that follow

for pkg in "$@"; do
    # Convert hyphens to underscores – the name we can import.
    import_name="${pkg//-/_}"

    #   4.1  Is the package already importable?
    if "$PYTHON_BIN" -c "import $import_name" 2>/dev/null; then
        version=$(_get_version "$pkg")
        echo "${pkg} already installed (version ${version})."
        continue
    fi

    #   4.2 Not present → install quietly.
    "$PYTHON_BIN" -m pip install -qq "$pkg"

    # Verify that the import now succeeds.
    if "$PYTHON_BIN" -c "import $import_name" 2>/dev/null; then
        version=$(_get_version "$pkg")
        echo "Installed ${pkg} ${version}."
    else
        echo "⚠️  ${pkg} was installed but cannot be imported."
    fi
done