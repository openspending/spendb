Installation and Setup
======================

Requirements
------------

* Python_ >= 2.7, with pip_ and virtualenv_   
* PostgreSQL_ >= 8.4
* RabbitMQ_ >= 2.6.1

.. _Python: http://www.python.org/
.. _PostgreSQL: http://www.postgres.org/
.. _RabbitMQ: http://www.rabbitmq.com//
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _pip: http://pypi.python.org/pypi/pip

Installation
------------

First, check out the source code from the repository, e.g. via git on 
the command line::

    $ git clone http://github.com/mapthemoney/spendb.git
    $ cd spendb

We also highly recommend you use a virtualenv_ to isolate the installed 
dependencies from the rest of your system.::

    $ virtualenv ./pyenv --distribute

Now activate the environment. Your prompt will be prefixed with the name of
the environment.::

    $ source ./pyenv/bin/activate

Ensure that any in shell you use to complete the installation you have run the 
preceding command.

Having the virtualenv set up, you can install SpenDB and its dependencies.
This should be pretty painless. Just run::

    $ pip install -r requirements.txt -e .

> For Windows users, run::
```
    $pip install -r windows_reqs.txt
```

You will also need to install python bindings for your database. For example,
for Postgresql you will want to install the psycopg2 library::

    $ pip install psycopg2

Create a database if you do not have one already. We recommend using Postgres
but you can use anything compatible with SQLAlchemy. For postgres you would do::

    $ createdb -E utf-8 --owner {your-database-user} spendb

Having done that, you can copy configuration templates::

    $ cp settings.py_tmpl settings.py
    $ export OPENSPENDING_SETTINGS=`pwd`/settings.py

Ensure that the ``SPENDB_SETTINGS`` environment variable is set whenever
you work with the application.

Edit the configuration files to make sure you're pointing to a valid database 
URL is set::

    # TCP
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pass}@localhost/spendb'

    or

    # Local socket
    SQLALCHEMY_DATABASE_URI = 'postgresql:///spendb'

Initialize the database::

    $ ostool db init

Generate the help system documentation (this is used by the front-end
and must be available, developer documents are separate). The output 
will be copied to the web applications template directory::

    $ git submodule init && git submodule update
    $ (cd doc && make clean html)

Compile the translations: ::

    $ python setup.py compile_catalog

Run the application::

    $ ostool runserver

In order to use web-based importing and loading, you will also need to set up
the celery-based background daemon. When running this, make sure to have an
instance of RabbitMQ installed and running and then execute::

    $ celery -A spendb.tasks worker -l info

You can validate the functioning of the communication between the backend and
frontend components using the ping action::

    $ curl -q http://localhost:5000/__ping__ >/dev/null

This should result in "Pong." being printed to the background daemon's console.

Test the install
----------------

Create test configuration (which inherits, by default, from `development.ini`): ::

    $ cp settings.py_tmpl test.py
    $ export SPENDB_SETTINGS=`pwd`/test.py

You will need to either set up a second instance of solr, or comment
out the solr url in settings file so that the tests use the same instance
of solr. Regrettably, the tests delete all data from solr when they
run, so having them share the development instance may be
inconvenient.

Run the tests.::

    $ nosetests 

Import a sample dataset: ::

    $ ostool csvimport --model https://dl.dropbox.com/u/3250791/sample-spendb-model.json http://mk.ucant.org/info/data/sample-spendb-dataset.csv
    $ ostool solr load spendb-example

Verify that the data is visible at http://127.0.0.1:5000/spendb-example/entries

Create an Admin User
--------------------

On the web user interface, register as a normal user. Once signed up, go into 
the database and do (replacing your-name with your login name)::

  UPDATE "account" SET admin = true WHERE "name" = 'username';

