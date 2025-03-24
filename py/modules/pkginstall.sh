#!/bin/bash

################################################################################
#
# Shell script to install python packages for Carto-Lab Docker base environment "worker_env"
# - provide list of package names as string, separated by space character
# - will check folder exists before installation, to reduce processing time
# - will output version of installed packages afterwards
#
################################################################################

# Exit as soon as a command fails
set -e

# Accessing an empty variable will yield an error
set -u

WORKER_PATH="/opt/conda/envs/worker_env/bin/python"
PACKAGE_PATH="/opt/conda/envs/worker_env/lib/python3.9/site-packages/"

pkgs=( $1 )
for i in "${!pkgs[@]}"; do
    if [ ! -d "${PACKAGE_PATH}${pkgs[i]}" ]
    then
        /opt/conda/envs/worker_env/bin/python -m pip install "${pkgs[i]}" >&- 2>&-
        pkgversion=$(/opt/conda/envs/worker_env/bin/python -c "import ${pkgs[i]//-/_};print(${pkgs[i]//-/_}.__version__);")
        echo "Installed ${pkgs[i]} ${pkgversion}."
        continue
    else
        echo "${pkgs[i]} already installed."
    fi
done
