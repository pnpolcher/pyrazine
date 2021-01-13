#!/bin/bash

set -e

PYTHON_VERSIONS=("3.6" "3.7" "3.8")

for python_version in "${PYTHON_VERSIONS[@]}"
do
  echo "Testing against Python ${python_version}"
  docker build -t pnpolcher-pyrazine:$python_version -f tests/Dockerfile . \
    --build-arg python_version=$python_version

  docker run -v `pwd`:/pyrazine -w /pyrazine pnpolcher-pyrazine:${python_version} nose2 -v

  docker run -v `pwd`:/pyrazine -w /pyrazine pnpolcher-pyrazine:${python_version} flake8
done