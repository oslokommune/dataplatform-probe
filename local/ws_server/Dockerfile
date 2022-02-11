# python:3.8-bullseye
FROM python@sha256:eb6bb612babb3bcb3b846e27904807f0fd2322b8d3d832b84dbc244f8fb25068
RUN mkdir /usr/src/app/
COPY . /usr/src/app/
WORKDIR /usr/src/app/
RUN pip install websockets
CMD ["python", "websocket_server.py"]
