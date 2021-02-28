ARG python_version
FROM lambci/lambda:python$python_version

USER root
RUN pip install -U aws_xray_sdk --no-cache-dir
