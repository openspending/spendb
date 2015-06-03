================
SpenDB API
================

Conventions
===========

Authentication
--------------

Some actions in SpenDB require authentication, particularly those that write to the system or aim to access protected data (e.g. pre-publication datasets). For this purpose, each user is provided an API key. The key is displayed in the *settings* (go to the dashboard and click on *Change* next to the Information header). You can use it to perform authentication by adding the following into the HTTP headers (change <your-api-key> to the API key you find in your settings)::

    Authorization: ApiKey <your-api-key>

JSON-P Callbacks
----------------

All API calls that return JSON support JSON-P (JSON with padding). You can 
add a ``?callback=foo`` parameter to any query to wrap the output in a 
function call. This is used to include JSON data in other sites that do not
support CORS::

    $ curl http://mapthemoney.org/cra.json?callback=foo

    foo({
        "description": "Data published by HM Treasury.", 
        "name": "cra", 
        "label": "Country Regional Analysis v2009", 
        "currency": "GBP"
    });

This can be used in remote web pages to include data as a simple ``script``
tag::

    <script>
      function foo(data) { 
        alert(data.label); 
      }
    </script>
    <script src="http://mapthemoney.org/cra.json?callback=foo"></script>

Aggregate API
=============

The data source used to drive visualizations is the Aggregate API. It 
can be used to flexibly generate aggregated views of the data by 
applying filters and grouping criteria.

This API is heavily based on OLAP concepts, and the documentation assumes 
you know `how we store data`_. As the API is based on Cubes, details on
the API call can be found in `the cubes documentation`_.

.. _how we store data: http://community.mapthemoney.org/help/guide/en/
.. _the cubes documentation: https://cubes.readthedocs.org/en/latest/server.html#aggregation-and-browsing

The full Cubes OLAP API is supported and available as part of the spendb
instance at::

  /api/slicer


Example: Where Does My Money Go?
--------------------------------

To highlight the use of this API, let's look at the UK Country
Regional Analysis dataset. This is a high-level survey of the 
UK budget, and the original `Where Does My Money Go?`_ page was based on this data. 

.. _Where Does My Money Go?: http://wheredoesmymoneygo.org

The first call we'll make will aggregate the complete dataset 
and give us a total sum (result: http://mapthemoney.org/api/2/aggregate?dataset=ukgov-finances-cra)::

    GET /api/slicer/cube/ukgov-finances-cra/aggregate

This is not very useful, however, as it includes UK spending 
over several years. So let's refine our query to include only
2010 figures (result: http://mapthemoney.org/api/2/aggregate?dataset=ukgov-finances-cra&cut=time.year:2010)::

    GET /api/slicer/cube/ukgov-finances-cra/aggregate?cut=time.year:2010

Much better! Now we may want to know how these funds are distributed
geographically, so let's drill down by the [NUTS](http://epp.eurostat.ec.europa.eu/portal/page/portal/nuts_nomenclature/introduction)
names of each region of the UK (result: http://mapthemoney.org/api/2/aggregate?dataset=ukgov-finances-cra&cut=time.year:2010&drilldown=region)::

    GET /api/slicer/cube/ukgov-finances-cra/aggregate?cut=time.year:2010&drilldown=region

Given an SVG file with the right region names, this could easily be
used to drive a CSS-based choropleth map, with a bit of JavaScript 
glue on the client side.

Another set of dimensions of the CRA dataset is the [Classification of 
Functions of Government (COFOG)](http://unstats.un.org/unsd/cr/registry/regcst.asp?Cl=4), 
which classifies government activity by its functional purpose. Like
many taxonomies, COFOG has several levels, which we have modelled as 
three dimensions: cofog1, cofog2 and cofog3.

In order to generate a Bubble Tree
diagram, we want to break down the full CRA dataset by each of these 
dimensions (result: http://mapthemoney.org/api/2/aggregate?dataset=ukgov-finances-cra&cut=time.year:2010&drilldown=cofog1|cofog2|cofog3)::

    GET /api/slicer/cube/ukgov-finances-cra/aggregate?cut=time.year:2010&drilldown=cofog1|cofog2|cofog3

(Warning: this generates quite a lot of data. You may want to paginate 
the results to view it in your browser.)

As you can see, the aggregator API can be used to flexibly query the 
data to generate views such as visualizations, maps or pivot tables.

REST Resources
==============

SpenDB pages generally support multiple representations, at least 
a user-facing HTML version and a JSON object that represents the contained
data. For various technical and non-technical reasons, most of the data is 
read-only.

Content negotiation can be performed either via HTTP ``Accept`` headers or 
via suffixes in the resource URL. The following types are generally 
recognized:

* **HTML** (Hyptertext Markup), MIME type ``text/html`` or any value not 
  otherwise in use, suffix ``.html``. This is the default representation.
* **JSON** (JavaScript Object Notation), MIME type ``application/json`` and
  suffix ``.json``.
* **CSV** (Comma-Separated Values), MIME type ``text/csv`` and suffix 
  ``.csv``. CSV is only supported where listings can be exported with some
  application-level meaning.

The key resources in SpenDB are datasets, entries, dimensions, and 
dimension members. Each of these has a listing and an entity view that can
be accessed.

Listing datasets
----------------

::

    GET /api/3/datasets

All datasets are listed, including their core metadata. Additionally, certain 
parameters are given as facets (i.e. territories and languages of the
datasets). Both ``territories`` and ``languages`` can also be passed in as 
query parameters to filter the result set. Supported formats are HTML, CSV and JSON.

::

    "territories": [
      /* ... */
      {
        "count": 2,
        "url": "/datasets?territories=BH",
        "code": "BH",
        "label": "Bahrain"
      },
      /* ... */
    ],
    "languages": /* Like territories. */
    "datasets": [
      {
        "name": "cra",
        "label": "Country Regional Analysis v2009",
        "description": "The Country Regional Analysis published by HM Treasury.",
        "currency": "GBP"
      },
      /* ... */
    ]

Getting dataset metadata
------------------------

::

    GET /api/3/datasets/{dataset}

Core dataset metadata is returned. This call does not have any 
parameters. Supported formats are HTML and JSON.

::

    {
      "name": "cra",
      "label": "Country Regional Analysis v2009",
      "description": "The Country Regional Analysis published by HM Treasury.",
      "currency": "GBP"
    }

Another call is available to get the full model description of 
the dataset in question, which includes the core metadata and also
a full description of all dimensions, measures, and views. The
format for this is always JSON::

    GET /{dataset}/model.json


Permissions API
===============

SpenDB allows users to check for their permissions on a given dataset via an API call. The response will provide the authenticated user's permission on as true or false values for *CRUD* (create, read, update, and delete). This API call mainly exists to allow software that uses the API (e.g. the loading API) to save bandwidth with big dataset updates.

For example if you as a developer are building a loading script that users of SpenDB can use to download data from a location and update datasets in SpenDB you might first run a check for permissions based on their API key before starting to download the updates (so you can skip it if they're not authorized).

The permission API works as follows. Make a *GET* request (wih user authenticated with the API key) to::

    /api/2/permissions?dataset=[dataset_name]

The response will be single json object with four properties, *create*, *read*, *update*, and *delete*. The value of each property is a boolean (true or false) that indicates if the authenticated user has that permission for the provided dataset::

    {
        "create": false,
        "read": true,
        "update": false,
        "delete": false
    }

Loading API
===========

Users can load datasets (or add sources to them) by making a *POST* request to ``/api/3/datasets`` (notice *https*) with the following url parameters:

* *csv_file* - A **url** to the csv file to me imported for the dataset
* *metadata* - A **url** to the json file with dataset metadata (name, currency, etc.) and the model. Views can also be defined in this file. Take a look at a sample json file - https://dl.dropbox.com/u/3250791/sample-spendb-model.json to see how it should be structured (the value for *mapping* is the model - how the csv file should be cast into dataset dimensions, and the value for *dataset* is the metadata itself). To gain a better understanding of how to do the mapping, take a look at the corresponding csv file - http://mk.ucant.org/info/data/sample-spendb-dataset.csv.
* *private* - A **boolean** ("true"/"false") indicating whether the loaded dataset should be private or not (made public). By default new datasets loaded via the API are made public. If an existing dataset is updated via the loading API the *private* parameter does nothing and the private setting is retained.

Along with these parameters an api key must be provided in the header of the request. For more details see [API Conventions](/help/api/conventions/).
