# python:3.10-bullseye
FROM python@sha256:536565e6d1d70f8d64cd054c796dbbf6abdcaaf85f4169b5715c7856a56ee903
RUN mkdir /usr/src/app/
COPY . /usr/src/app/
WORKDIR /usr/src/app/
RUN pip install websockets
CMD ["python", "websocket_server.py"]
