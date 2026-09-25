#!/usr/bin/env bash
#  Quiet, root‑warning‑free Python package installer
#  (shows one line per package – already installed / installed)

set -euo pipefail                     # fail fast, treat unset vars as errors

# 1  Suppress the “Running pip as the 'root' user …” warning
export PIP_ROOT_USER_ACTION=ignore

# 2  Mapping for packages whose PyPI distribution name differs from the CLI name
declare -A DIST_NAME_MAP=(
    [dotenv]="python-dotenv"
    [adjusttext]="adjustText"
)

# 3  Mapping for packages whose Python import name differs from the CLI name
declare -A IMPORT_NAME_MAP=(
    [adjusttext]="adjustText"
    [python-dotenv]="dotenv"
)

# 4  Helper: ask the same interpreter ($PYTHON_BIN) for a version
_get_version() {
    local pkg="$1"
    local dist_name="${DIST_NAME_MAP[$pkg]:-$pkg}"

    "$PYTHON_BIN" - <<PY
import importlib.metadata as meta
import sys

dist = "${dist_name}"
try:
    print(meta.version(dist))
except meta.PackageNotFoundError:
    try:
        mod = __import("${IMPORT_NAME_MAP[$pkg]:-${pkg//-/_}}")
        print(getattr(mod, "__version__", "unknown"))
    except Exception:
        print("unknown")
except Exception as e:
    print("unknown")
PY
}

# 5  Main loop
PYTHON_BIN="$1"
shift                     # now $@ holds the list of packages that follow

for pkg in "$@"; do
    # Resolve the actual Python import name (with fallback)
    import_name="${IMPORT_NAME_MAP[$pkg]:-${pkg//-/_}}"
    # Resolve the actual PyPI install name
    dist_name="${DIST_NAME_MAP[$pkg]:-$pkg}"

    # 5.1 Is the package already importable?
    if "$PYTHON_BIN" -c "import $import_name" 2>/dev/null; then
        version=$(_get_version "$pkg")
        echo "${pkg} already installed (version ${version})."
        continue
    fi

    # 5.2 Not present → install using the proper distribution name
    "$PYTHON_BIN" -m pip install -qq "$dist_name"

    # Verify that the import now succeeds
    if "$PYTHON_BIN" -c "import $import_name" 2>/dev/null; then
        version=$(_get_version "$pkg")
        echo "Installed ${pkg} ${version}."
    else
        echo "⚠️  ${pkg} was installed but cannot be imported as '${import_name}'."
    fi
done