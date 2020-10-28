FROM python:3.8
RUN pip install pipenv

WORKDIR /usr/src/app/workdir
COPY Pipfile ./
COPY Pipfile.lock ./
COPY resources ./resources
RUN pipenv install --deploy --ignore-pipfile

COPY probe ./probe

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["pipenv", "run", "app"]