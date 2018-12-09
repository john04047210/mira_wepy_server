FROM python:3.5-slim

ENV INVENIO_WEB_HOST=127.0.0.1
ENV INVENIO_WEB_INSTANCE=invenio
ENV INVENIO_WEB_VENV=invenio
ENV INVENIO_REDIS_HOST=wepy_redis
ENV INVENIO_CACHE_REDIS_URL=redis://wepy_redis:6379/1
ENV INVENIO_CACHE_DEFAULT_TIMEOUT=3600
ENV INVENIO_POSTGRESQL_HOST=db
ENV INVENIO_POSTGRESQL_DBNAME=wepy
ENV INVENIO_POSTGRESQL_DBUSER=wepy
ENV INVENIO_POSTGRESQL_DBPASS=wepy!1234
ENV INVENIO_SQLALCHEMY_DATABASE_URI=postgresql://wepy:wepy!1234@db/wepy
ENV INVENIO_WORKER_HOST=127.0.0.1

WORKDIR /code
RUN mkdir -p /code/modules
RUN apt-get -y update
RUN apt-get -y install git
RUN cd /code && git clone https://github.com/inveniosoftware/invenio.git invenio
RUN cd invenio && pip install . && pip install .[postgresql]

EXPOSE 5000
CMD ["/bin/bash", "-c", "invenio run -h 0.0.0.0"]
