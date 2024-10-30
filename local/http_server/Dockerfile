# python:3.13-slim-bookworm
FROM python@sha256:751d8bece269ba9e672b3f2226050e7e6fb3f3da3408b5dcb5d415a054fcb061

RUN mkdir /usr/src/app/
COPY . /usr/src/app/
WORKDIR /usr/src/app/
RUN pip install flask
CMD ["python", "http_server.py"]
