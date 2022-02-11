# python:3.8-bullseye
FROM python@sha256:eb6bb612babb3bcb3b846e27904807f0fd2322b8d3d832b84dbc244f8fb25068

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
