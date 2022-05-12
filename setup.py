from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dataplatform-probe",
    version="0.1.0",
    author="Origo Dataplattform",
    author_email="dataplattform@oslo.kommune.no",
    description="Monitoring service for dataplatform services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oslokommune/dataplatform-probe",
    packages=find_packages(),
    install_requires=[
        "aws-xray-sdk",
        "okdata-sdk",
        "prometheus-client",
        "requests",
    ],
)
