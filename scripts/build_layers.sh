#!/bin/bash

set -e

LAYER_DIR=".layers"
LAYER_FILE_PREFIX="pyrazine"
PYTHON_VERSIONS=("3.6" "3.7" "3.8")

function build_layer {
  destination=$(realpath "$2")

  temp_dir=$(mktemp -d)
  docker build -t pnpolcher-pyrazine-layer:"$1" . --no-cache \
      --build-arg python_version="$1" \
      --build-arg runtime="python${python_version}"

  docker run --rm pnpolcher-pyrazine-layer:"$1" tar cf - python | tar -xf - -C $temp_dir

  (cd "$temp_dir" && zip -q -r "$destination" ./)

  rm -rf "$temp_dir"
  echo "Created layer file for Python version $1."
}

rm -rf $LAYER_DIR
mkdir $LAYER_DIR

for python_version in "${PYTHON_VERSIONS[@]}"
do
    echo "Building layer for python version $python_version"
    build_layer "${python_version}" ${LAYER_DIR}/${LAYER_FILE_PREFIX}"${python_version}".zip
done
