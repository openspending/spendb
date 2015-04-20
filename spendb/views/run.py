import logging

from flask import Blueprint, render_template
# from flask.ext.babel import gettext as _
# from werkzeug.exceptions import BadRequest
from apikit import obj_or_404

from openspending.model.run import Run
from openspending.auth import require
from openspending.lib.helpers import get_dataset, get_page
# from openspending.lib.pagination import Page
from openspending.views.cache import disable_cache

log = logging.getLogger(__name__)
blueprint = Blueprint('run', __name__)


def get_run(dataset, id):
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)
    run = obj_or_404(Run.by_id(id))
    return dataset, run


@blueprint.route('/<dataset>/runs/<id>', methods=['GET'])
def view(dataset, id, format='html'):
    disable_cache()
    dataset, run = get_run(dataset, id)
    # system = run.records.filter_by(category=LogRecord.CATEGORY_SYSTEM)
    # num_system = system.count()
    # system_page = Page(system.order_by(LogRecord.timestamp.asc()),
    #                    page=get_page('system_page'),
    #                    items_per_page=10)
    # data = run.records.filter_by(category=LogRecord.CATEGORY_DATA)
    # num_data = data.count()
    # data_page = Page(data.order_by(LogRecord.timestamp.asc()),
    #                  page=get_page('data_page'),
    #                  items_per_page=20)
    return render_template('run/view.html', dataset=dataset,
                           run=run, num_system=num_system,
                           system_page=system_page, num_data=num_data,
                           data_page=data_page)
