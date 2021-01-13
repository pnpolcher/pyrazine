ARG python_version
FROM python:$python_version

ENV PYTHONDONTWRITEBYTECODE True

RUN mkdir -p /test
WORKDIR /test

COPY . .
RUN pip install .[dev]

