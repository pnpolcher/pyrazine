#!/bin/bash

set -e

PYTHON_VERSIONS=("3.6" "3.7" "3.8")
BASE_DIR=`pwd`
LAYER_DIR=$BASE_DIR/.layer_data
rm -Rf $LAYER_DIR

for python_version in "${PYTHON_VERSIONS[@]}"
do
  echo "Testing against Python ${python_version}"

  LAYER_DATA_DIR="$LAYER_DIR/$python_version"
  mkdir -p $LAYER_DATA_DIR
  cd $LAYER_DATA_DIR
  unzip $BASE_DIR/.layers/pyrazine${python_version}.zip
  cd $BASE_DIR

  docker run \
    -v `pwd`/tests/integration:/var/task \
    -v $LAYER_DATA_DIR:/opt:ro,delegated \
    "lambci/lambda:python${python_version}" \
    test_lambda.lambda_handler
done
