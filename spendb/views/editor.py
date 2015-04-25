import logging
import json
from datetime import datetime

from flask import Blueprint, render_template, redirect, request
from flask.ext.login import current_user
from flask.ext.babel import gettext as _
from werkzeug.exceptions import BadRequest
from colander import Invalid

from spendb.core import db, data_manager
from spendb.model import Account, Run
from spendb.auth import require
from spendb.lib.helpers import url_for, get_dataset
from spendb.lib.helpers import flash_success
from spendb.reference import CURRENCIES
from spendb.reference import COUNTRIES
from spendb.reference import CATEGORIES
from spendb.reference import LANGUAGES
from spendb.validation.dataset import dataset_schema
from spendb.validation.mapping import mapping_schema
from spendb.validation.common import ValidationState
from spendb.views.cache import disable_cache

log = logging.getLogger(__name__)
blueprint = Blueprint('editor', __name__)


@blueprint.route('/datasets/<dataset>/editor', methods=['GET'])
def index(dataset):
    disable_cache()
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)

    entries_count = dataset.fact_table.num_entries()
    package = data_manager.package(dataset.name)
    sources = sorted(package.sources, key=lambda s: s.meta.get('created_at'))
    has_sources = len(sources) > 0
    source = sources[0] if has_sources else None
    return render_template('editor/index.html', dataset=dataset,
                           entries_count=entries_count,
                           has_sources=has_sources, source=source)


@blueprint.route('/datasets/<dataset>/editor/team', methods=['GET'])
def team_edit(dataset, errors={}, accounts=None):
    disable_cache()
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)

    accounts = accounts or dataset.managers
    accounts = [a.to_dict() for a in accounts]
    errors = errors
    return render_template('editor/team.html', dataset=dataset,
                           accounts=accounts, errors=errors)


@blueprint.route('/datasets/<dataset>/editor/team', methods=['POST'])
def team_update(dataset):
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)

    errors, accounts = {}, []
    for account_name in request.form.getlist('accounts'):
        account = Account.by_name(account_name)
        if account is None:
            errors[account_name] = _("User account cannot be found.")
        else:
            accounts.append(account)
    if current_user not in accounts:
        accounts.append(current_user)

    if not len(errors):
        dataset.managers = accounts
        dataset.updated_at = datetime.utcnow()
        db.session.commit()
        flash_success(_("The team has been updated."))
    return team_edit(dataset.name, errors=errors, accounts=accounts)

