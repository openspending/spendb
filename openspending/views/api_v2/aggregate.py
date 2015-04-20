import logging

from flask import request

from openspending.core import cache
from openspending.auth import require
from openspending.lib.util import cache_hash
from openspending.lib.jsonexport import jsonify
from openspending.lib.paramparser import AggregateParamParser
from openspending.inflation.aggregation import aggregate as inf_aggregate
from openspending.lib.hypermedia import drilldowns_apply_links
from openspending.views.cache import etag_cache_keygen
from openspending.views.api_v2.common import blueprint


log = logging.getLogger(__name__)


@cache.memoize()
def cached_aggregate(dataset, measures=['amount'], drilldowns=None, cuts=None,
                     page=1, pagesize=10000, order=None, inflate=None):
    """ A proxy object to run cached calls against the dataset
    aggregation function. This is neither a concern of the data
    model itself, nor should it be repeated at each location
    where caching of aggregates should occur - thus it ends up
    here.
    For call docs, see ``model.Dataset.aggregate``. """
    return inf_aggregate(dataset, measures=measures,
                         drilldowns=drilldowns, cuts=cuts,
                         page=page, pagesize=pagesize,
                         order=order, inflate=inflate)

cached_aggregate.make_cache_key = cache_hash


@blueprint.route('/api/2/aggregate')
def aggregate():
    """
    Aggregation of a dataset based on URL parameters. It serves the
    aggregation from a cache if possible, and if not it computes it (it's
    performed in the aggregation cache for some reason).
    """

    # Parse the aggregation parameters to get them into the right format
    parser = AggregateParamParser(request.args)
    params, errors = parser.parse()

    # If there were parsing errors we return them with status code 400
    # as jsonp, irrespective of what format was asked for.
    if errors:
        return jsonify({'errors': errors}, status=400)

    # URL parameters are always singular nouns but we work with some
    # as plural nouns so we pop them into the plural version
    params['cuts'] = params.pop('cut')
    params['drilldowns'] = params.pop('drilldown')
    params['measures'] = params.pop('measure')

    # Get the dataset and the format and remove from the parameters
    dataset = params.pop('dataset')

    # User must have the right to read the dataset to perform aggregation
    require.dataset.read(dataset)

    try:
        # Create an aggregation cache for the dataset and aggregate its
        # results. The cache will perform the aggreagation if it doesn't
        # have a cached result.
        result = cached_aggregate(dataset, **params)

        # If the result has drilldown we create html_url values for its
        # dimensions (linked data).
        if 'drilldown' in result:
            result['drilldown'] = drilldowns_apply_links(
                dataset.name, result['drilldown'])

        # Do the ETag caching based on the cache_key in the summary
        # this is a weird place to do it since the heavy lifting has
        # already been performed above. TODO: Needs rethinking.
        etag_cache_keygen(dataset)

    except (KeyError, ValueError) as ve:
        # We log possible errors and return them with status code 400
        log.exception(ve)
        return jsonify({'errors': [unicode(ve)]}, status=400)

    return jsonify(result)
