#!/bin/bash
set -e

# Locate the launch.py file
LAUNCH_PY=$(python -c "import sphinx_book_theme, os; print(os.path.join(os.path.dirname(sphinx_book_theme.__file__), 'header_buttons', 'launch.py'))")

echo "Patching launch.py at: $LAUNCH_PY"

# Safely insert query params, preserving indentation
sed -i '/url = f"{url}?urlpath=/a \        url += "&flavor=xl1nfdi&system=JSC-Cloud"' "$LAUNCH_PY"

# change button label
sed -i 's/"text": "Binder"/"text": "Jupyter4NFDI"/' "$LAUNCH_PY"
sed -i 's/"Launch on" \+ " Binder"/"Launch on Jupyter4NFDI"/' "$LAUNCH_PY"

echo "Patch applied successfully."
