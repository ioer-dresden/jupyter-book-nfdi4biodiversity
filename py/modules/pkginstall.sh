#!/bin/bash

################################################################################
#
# Environment-agnostic Python package installer.
# - Use the Python binary passed as first argument
# - Check if each package is available; install it if not
#
################################################################################

set -e
set -u

PYTHON_BIN="$1"
shift  # Shift arguments so $@ now contains only packages

pkgs=( "$@" )

for pkg in "${pkgs[@]}"; do
    import_name="${pkg//-/_}"
    if "$PYTHON_BIN" -c "import ${import_name}" 2>/dev/null; then
        version=$("$PYTHON_BIN" -c "import ${import_name}; print(getattr(${import_name}, '__version__', 'unknown'))")
        echo "${pkg} already installed (version ${version})."
    else
        echo "Installing ${pkg}..."
        "$PYTHON_BIN" -m pip install "$pkg" --quiet
        if "$PYTHON_BIN" -c "import ${import_name}" 2>/dev/null; then
            version=$("$PYTHON_BIN" -c "import ${import_name}; print(getattr(${import_name}, '__version__', 'unknown'))")
            echo "Installed ${pkg} ${version}."
        else
            echo "Warning: ${pkg} installed but version could not be determined."
        fi
    fi
done