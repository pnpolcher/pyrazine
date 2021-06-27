import os
from setuptools import setup

from pyrazine import __version__

cwd = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(cwd, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="pyrazine",
    version=__version__,
    description="A lightweight layer to simplify writing microservices on AWS Lambda",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pnpolcher/pyrazine",
    author="Pablo Nuñez Pölcher",
    author_email="info@pablopolcher.dev",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="pyrazine aws lambda layer",
    packages=[
        "pyrazine",
        "pyrazine.auth",
        "pyrazine.handlers",
        "pyrazine.requests",
        "pyrazine.typing",
        "pyrazine.serdes",
    ],
    python_requires=">=3.6, <4",
    install_requires=[
        "setuptools==51.0.0"
    ],
    extras_require={
        "dev": ["flake8==3.8.4", "nose2==0.9.2"]
    },
)
