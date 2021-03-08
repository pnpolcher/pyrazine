ARG python_version
FROM python:$python_version

ARG runtime

RUN mkdir -p /build/python/lib/$runtime/site-packages
WORKDIR /build

RUN pip install aws-xray-sdk python-jose -t ./python/lib/$runtime/site-packages
COPY . .
RUN pip install . -t ./python/lib/$runtime/site-packages

RUN find ./python/lib/$runtime/site-packages -name \*.pyc -delete

RUN rm -rf ./python/lib/$runtime/site-packages/botocore*
