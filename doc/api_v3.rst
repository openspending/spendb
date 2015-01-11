===========================
OpenSpending API, Version 3
===========================


* GET /api/3/reference - static reference data (countries, currencies etc)
* GET /api/3/datasets - dataset listing
* POST /api/3/datasets - create a dataset
* GET /api/3/datasets/<name> - get basic metadata
* POST /api/3/datasets/<name> - write basic metadata (also: public/private)
* DELETE /api/3/datasets/<name> - delete a whole dataset
* GET /api/3/datasets/<name>/model - get dataset model
* POST /api/3/datasets/<name>/model - write model
* GET /api/3/datasets/<name>/managers - manager accounts
* POST /api/3/datasets/<name>/managers - edit access rights
* GET /api/3/datasets/<name>/managers - manager accounts
* POST /api/3/datasets/<name>/managers - edit access rights
* GET /api/3/datasets/<name>/sources - list existing sources
* POST /api/3/datasets/<name>/sources - create a new source and begin loading
* GET /api/3/datasets/<name>/runs - list runs for a dataset
* GET /api/3/datasets/<name>/runs/<id> - get details for a run, including the log
