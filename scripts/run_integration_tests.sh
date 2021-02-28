#!/bin/bash

set -e

# PYTHON_VERSIONS=("3.6" "3.7" "3.8")
PYTHON_VERSIONS=("3.8")
BASE_DIR=`pwd`
LAYER_DIR=$BASE_DIR/.layer_data
rm -Rf $LAYER_DIR
AWS_REGION="eu-west-1"

for python_version in "${PYTHON_VERSIONS[@]}"
do
  echo "Testing against Python ${python_version}"

  LAYER_DATA_DIR="$LAYER_DIR/$python_version"
  mkdir -p $LAYER_DATA_DIR
  cd $LAYER_DATA_DIR
  unzip $BASE_DIR/.layers/pyrazine${python_version}.zip
  cd $BASE_DIR

  docker build -t pnpolcher/pyrazine-integration-tests:$python_version \
               -f tests/integration/Dockerfile . \
               --build-arg python_version=$python_version

  # Start the container with the test Lambda function.
#  docker run \
#    -v `pwd`/tests/integration:/var/task:ro,delegated \
#    -v $LAYER_DATA_DIR:/opt:ro,delegated \
#    "pnpolcher/pyrazine-integration-tests:${python_version}" \
#    test_lambda.lambda_handler '{}'

  XRAY_IP=$(docker network inspect bridge | jq -r .[].IPAM.Config[0].Gateway)
  CONTAINER_HASH=$(docker run --rm -d \
    -p 9001:9001 \
    -e DOCKER_LAMBDA_STAY_OPEN=1 \
    -e AWS_XRAY_DAEMON_ADDRESS="${XRAY_IP}:2000" \
    -e _AWS_XRAY_DAEMON_ADDRESS="${XRAY_IP}" \
    -e _AWS_XRAY_DAEMON_PORT=2000 \
    -v `pwd`/tests/integration:/var/task:ro,delegated \
    -v $LAYER_DATA_DIR:/opt:ro,delegated \
    "pnpolcher/pyrazine-integration-tests:${python_version}" \
    test_lambda.lambda_handler)

  PAYLOAD=$(pipenv run python ./tests/integration/inject_jwt.py test_get.json)
  LOG_RESULT=$(aws lambda invoke \
    --endpoint http://localhost:9001 \
    --no-sign-request \
    --region $AWS_REGION \
    --cli-binary-format raw-in-base64-out \
    --function-name test_lambda \
    --log-type Tail \
    --payload "$PAYLOAD" \
    output.json \
    | jq -r .LogResult \
    | python -c "import base64; import sys; print(base64.b64decode(sys.stdin.read()).decode('utf-8'))")

  echo "${LOG_RESULT}"

  docker stop "$CONTAINER_HASH"

done
