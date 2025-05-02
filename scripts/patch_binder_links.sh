#!/bin/bash
set -e

# Locate the launch.py file in the sphinx_book_theme package
LAUNCH_PY=$(python -c "import sphinx_book_theme, os; print(os.path.join(os.path.dirname(sphinx_book_theme.__file__), 'header_buttons', 'launch.py'))")

echo "Patching launch.py at: $LAUNCH_PY"

# Use sed to modify the URL construction line to add custom query parameters
# This will insert '&flavor=xl1nfdi&system=JSC-Cloud' after 'urlpath=...'
sed -i.bak 's/\(url = f"{url}\?urlpath=.*"\)/\1 + "&flavor=xl1nfdi&system=JSC-Cloud"/' "$LAUNCH_PY"

echo "Patch applied successfully."
