# python:3.8-bullseye
FROM python@sha256:1fbd81716d6d8d6081b11b058894533e36c93abd10d91560ac8011a27ca13947

WORKDIR /usr/src/app/workdir
COPY requirements.txt ./
ENV VIRTUAL_ENV=/opt/.venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -r requirements.txt

COPY probe ./probe

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "-m", "probe"]
