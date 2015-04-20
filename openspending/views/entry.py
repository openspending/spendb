import logging

from flask import Blueprint, render_template, redirect, request
from flask.ext.babel import gettext as _
from werkzeug.exceptions import BadRequest

from openspending.lib.hypermedia import entry_apply_links
from openspending.lib.helpers import url_for, get_dataset, flash_notice
from openspending.lib.jsonexport import jsonify
from openspending.inflation import inflate
from openspending.lib.pagination import Page

log = logging.getLogger(__name__)
blueprint = Blueprint('entry', __name__)


@blueprint.route('/<dataset>/entries')
@blueprint.route('/<dataset>/entries.<fmt:format>')
def index(dataset, format='html'):
    dataset = get_dataset(dataset)
    return render_template('entry/index.html')


@blueprint.route('/<dataset>/entries/<nodot:id>')
@blueprint.route('/<dataset>/entries/<nodot:id>.<fmt:format>')
def view(dataset, id, format='html'):
    """
    Get a specific entry in the dataset, identified by the id. Entry
    can be return as html (default), json or csv.
    """
    dataset = get_dataset(dataset)

    # Get the entry that matches the given id. dataset.entries is
    # a generator so we create a list from it's responses based on the
    # given constraint
    cond = dataset.fact_table.alias.c._id == id
    entries = list(dataset.fact_table.entries(cond))
    # Since we're trying to get a single entry the list should only
    # contain one entry, if not then we return an error
    if not len(entries) == 1:
        raise BadRequest(_('Sorry, there is no entry %(id)s', id=id))

    # Add urls to the dataset and assign assign it as a context variable
    entry = entry_apply_links(dataset.name, entries.pop())

    tmpl_context = {
        'dataset': dataset,
        'entry': entry,
        'amount': entry.get('amount')
    }

    # We adjust for inflation if the user as asked for this to be inflated
    if 'inflate' in request.args:
        try:
            # Inflate the amount. Target date is provided in request.params
            # as value for inflate and reference date is the date of the
            # entry. We also provide a list of the territories to extract
            # a single country for which to do the inflation
            inflation = inflate(tmpl_context.get('amount'),
                                request.args['inflate'],
                                entry.get('time'),
                                dataset.territories)

            # The amount to show should be the inflated amount
            # and overwrite the entry's amount as well
            tmpl_context['amount'] = inflation['inflated']
            tmpl_context['entry']['amount'] = inflation['inflated']

            # We include the inflation response in the entry's dict
            # HTML description assumes every dict value for the entry
            # includes a label so we include a default "Inflation
            # adjustment" for it to work.
            inflation['label'] = 'Inflation adjustment'
            tmpl_context['entry']['inflation_adjustment'] = inflation
            tmpl_context['inflation'] = inflation
        except Exception:
            # If anything goes wrong in the try clause (and there's a lot
            # that can go wrong). We just say that we can't adjust for
            # inflation and set the context amount as the original amount
            flash_notice(_('Unable to adjust for inflation'))

    # Add the rest of the dimensions relating to this entry into a
    # extras dictionary. We first need to exclude all dimensions that
    # are already shown and then we can loop through the dimensions
    excluded_keys = ('time', 'amount', 'currency', 'from',
                     'to', 'dataset', 'id', 'name', 'description')

    extras = {}
    if dataset:
        # Create a dictionary of the dataset dimensions
        desc = dict([(d.name, d) for d in dataset.model.dimensions])
        tmpl_context['desc'] = desc
        # Loop through dimensions of the entry
        for key in entry:
            # Entry dimension must be a dataset dimension and not in
            # the predefined excluded keys
            if key in desc and key not in excluded_keys:
                extras[key] = entry[key]

    tmpl_context['extras'] = extras

    # Return entry based on
    if format == 'json':
        return jsonify(entry)
    else:
        return render_template('entry/view.html', **tmpl_context)


@blueprint.route('/search')
def search():
    return render_template('entry/search.html')
