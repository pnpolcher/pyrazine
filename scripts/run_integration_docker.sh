PYTHON_VERSION=3.8
LAYER_DATA_DIR=$(pwd)/.layer_data/"${PYTHON_VERSION}"

docker run --rm -d \
  -p 9001:9001 \
  -e DOCKER_LAMBDA_STAY_OPEN=1 \
  -e AWS_XRAY_DAEMON_ADDRESS=127.0.0.1:2000 \
  -e _AWS_XRAY_DAEMON_ADDRESS=127.0.0.1 \
  -e _AWS_XRAY_DAEMON_PORT=2000 \
  -v "`pwd`"/tests/integration:/var/task:ro,delegated \
  -v $LAYER_DATA_DIR:/opt:ro,delegated \
  "pnpolcher/pyrazine-integration-tests:${PYTHON_VERSION}" \
  test_lambda.lambda_handler
