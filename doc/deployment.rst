Deployment practices
====================

The target platform of SpenDB is Ubuntu Lucid Lynx (10.04) LTS. While
the software can be installed on other systems (OS X is used on a daily 
basis, Windows may be a stretch), the following guide will refer to 
dependencies by their Ubuntu package name.

Installing the software
'''''''''''''''''''''''

This guide is intended as a complement to :doc:`install`, so a basic
familiarity with the installation procedure and configuration options is
assumed. The key differences in a production install are these:

* We usually install SpenDB as user ``okfn`` in ``~/var/srvc/<site>``,
  where the installation root is a ``virtualenv``.
* As a database, we'll always use PostgreSQL (version 9.1 for production).
  This also means we need to install the ``psycopg2`` python bindings used
  by SQLALchemy. The server is installed and set up by creating a user and 
  initial database::
    
    # apt-get install postgres
    # su postgres
    $ createuser -D -P -R -S spendb
    Password:
    $ createdb -E utf8 -O spendb -T template0 spendb.mapthemoney.org

* To install the core software and dependencies, a pip file is created as
  ``pip-site.txt`` with the following contents::

    psycopg2
    gunicorn
    -e git+http://github.com/spendb/spendb#egg=spendb

  This means that updates can be installed easily and quickly by running
  the same command used for the initial setup::

    (env)~/var/srvc/spendb.mapthemoney.org$ pip install -r pip-site.txt

* Set up related git modules, help, and catalogs in src/spendb, as in :doc:`install`.

* Set up ``settings.py`` as in :doc:`install`, and make sure the environment
  variable ``SPENDB_SETTINGS`` is set correctly.

* Set up the database: ::

  $ spendb db init

* Start celery workers (e.g. on a backend machine). Celery will configure
  itself based on the relevant settings in the configuration script::

    CELERY_BROKER_URL = 'amqp://backend.server.com:5672/'

  It is likely that you set this up so that the celery workers use a localhost
  broker url (rabbitmq installed on the same machine as the celery worker
  instance) while the frontend (web app) machine needs a broker url that points
  to that backend machine.

  Then start up celery by setting ``SPENDB_SETTINGS`` (can be managed by
  supervisor)::

    (env)~/spendb$ celery -A spendb.tasks -l info worker

* The application is run through ``gunicorn`` (Green Unicorn), a fast, 
  pre-fork based HTTP server for WSGI applications (remember to set the
  ``SPENDB_SETTINGS`` environment variable)::

    (env)~/var/srvc/spendb.mapthemoney.org$ gunicorn spendb.core:create_web_app

  To determine the number of workers and the port to listen on, a
  configuration file called ``gunicorn-config.py`` is created with
  basic settings::

    import multiprocessing
    bind = "127.0.0.1:18000"
    workers = multiprocessing.cpu_count() * 2 + 1

  This can be passed using the ``-c`` argument::

    (env)~/var/srvc/spendb.mapthemoney.org$ gunicorn -c gunicorn-config.py spendb.core:create_web_app

* In order to make sure gunicorn is automatically started, monitored, and run
  with the right arguments, ``supervisord`` is installed::

    # apt-get install supervisor

  After installing supervisor, a new configuration file can be dropped into 
  ``/etc/supervisor/conf.d/spendb.mapthemoney.org.conf`` with the following basic
  contents::

    [program:spendb.mapthemoney.org]
    command=/home/okfn/var/srvc/spendb.mapthemoney.org/bin/gunicorn spendb.core:create_web_app -c /home/okfn/var/srvc/spendb.mapthemoney.org/gunicorn-config.py
    directory=/home/okfn/var/srvc/spendb.mapthemoney.org/
    environment=OPENSPENDING_SETTINGS='/home/okfn/var/srvc/spendb.mapthemoney.org/settings.py'
    user=www-data
    autostart=true
    autorestart=true
    stdout_logfile=/home/okfn/var/srvc/spendb.mapthemoney.org/logs/supervisord.log
    redirect_stderr=true

  For logging, this required that you create the logs directory in the site 
  install, with permissions for ``www-data`` to write it.

  Supervisor can be started as a daemon::

    # /etc/init.d/supervisor start

* Finally, ``nginx`` is used as a front-end web server through which the
  application is proxied and static files are served. Install ``nginx`` as 
  a normal package::

    # apt-get install nginx

  A configuration can be created at ``/etc/nginx/sites-available/spendb``
  and later symlinked over into the ``sites-enabled`` folder. The host will 
  contain a server name, static path and a reference to the upstream
  ``gunicorn`` server::

      upstream app_server {
        server 127.0.0.1:18000;
      }

      server {
        listen 80;
        server_name spendb.mapthemoney.org;

        access_log /var/log/nginx/spendb.mapthemoney.org-access.log;
        error_log /var/log/nginx/spendb.mapthemoney.org-error.log notice;
        
        location /static {
          alias /home/okfn/var/srvc/spendb.mapthemoney.org/src/spendb/spendb/static;
        }

        location / {
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header Host $http_host;
          proxy_redirect off;
          proxy_pass http://app_server;
          break;
        }
      }

  In a completely unexpected turn of events, ``nginx`` can be started 
  as a daemon::

    # /etc/init.d/nginx start
