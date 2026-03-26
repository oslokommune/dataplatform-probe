# python:3.13-slim-trixie
FROM python@sha256:739e7213785e88c0f702dcdc12c0973afcbd606dbf021a589cab77d6b00b579d

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

RUN groupadd -r app
RUN useradd -r -g app app
RUN chown -R app:app /usr/src/app/workdir
USER app

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "-m", "probe"]
