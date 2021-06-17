FROM python:3.8
RUN mkdir /usr/src/app/
COPY . /usr/src/app/
WORKDIR /usr/src/app/
RUN pip install flask websocket-client
CMD ["python", "http_server.py"]
