FROM ubuntu:14.04
MAINTAINER Francesco Siddi <francesco@blender.org>

RUN apt-get update && apt-get install -y \
python \
python-dev \
python-pip \
libmysqlclient-dev \
zlib1g-dev \
libjpeg-dev \
nano \
python-crypto \
python-openssl \
libssl-dev \
libffi-dev

RUN mkdir -p /data/git/blender-id \
&& mkdir -p /data/storage

RUN pip install virtualenv \
&& virtualenv /data/venv

ENV PIP_PACKAGES_VERSION 1
ADD requirements.txt /requirements.txt

RUN . /data/venv/bin/activate \
&& pip install -U pip && pip install -r /requirements.txt

VOLUME /data/git/blender-id
VOLUME /data/storage

EXPOSE 8000

ENV BUILD_VERSION 1

ADD runserver.sh /runserver.sh
ADD manage.sh /manage.sh

ENTRYPOINT ["bash", "/runserver.sh"]
