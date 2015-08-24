FROM pudo/deb-flask-node
MAINTAINER Friedrich Lindenberg <friedrich@pudo.org>

ENV DEBIAN_FRONTEND noninteractive

RUN echo 'deb http://ftp.de.debian.org/debian wheezy-backports main' >> /etc/apt/sources.list \
  && apt-get update -qq \
  && apt-get install -y -q --no-install-recommends \
        git python2.7 python-pip build-essential python-dev \
        libxml2-dev libxslt1-dev libpq-dev curl apt-utils ca-certificates \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN curl -L https://www.npmjs.org/install.sh | sh
RUN npm install -g bower

# Use clean checkout because ADD implodes on symlinks.
RUN git clone https://github.com/spendb/spendb.git /spendb
WORKDIR /spendb

ADD prod_settings.py settings.py
ENV SPENDB_SETTINGS /spendb/settings.py
RUN pip install functools32 && pip install -r requirements.txt -e /spendb

EXPOSE 8000
