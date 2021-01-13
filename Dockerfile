ARG python_version
FROM python:$python_version

ARG runtime

RUN mkdir -p /build/python/lib/$runtime/site-packages
WORKDIR /build

COPY . .
RUN pip install . -t ./python/lib/$runtime/site-packages

RUN find ./python/lib/$runtime/site-packages -name \*.pyc -delete

RUN rm -rf ./python/lib/$runtime/site-packages/botocore*
