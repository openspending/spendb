import colander
from flask import Blueprint, render_template, request, redirect
from flask.ext.login import current_user, login_user, logout_user
from flask.ext.babel import gettext as _
from sqlalchemy.sql.expression import or_
from werkzeug.security import check_password_hash, generate_password_hash
from apikit import obj_or_404, Pager, jsonify

from spendb.core import db, login_manager, url_for
from spendb.auth import require
from spendb.model import Account, Dataset
from spendb.validation.account import AccountRegister, AccountSettings
from spendb.lib.mailer import send_reset_link
from spendb.lib.helpers import flash_error, flash_success
from spendb.views.cache import disable_cache


blueprint = Blueprint('account', __name__)


@blueprint.route('/dashboard')
def dashboard(format='html'):
    """
    Show the user profile for the logged in user
    """
    disable_cache()
    require.account.logged_in()
    return profile(current_user.name)


@blueprint.route('/account/<account>')
def profile(account):
    """ Generate a profile page for a user (from the provided name) """
    profile = obj_or_404(Account.by_name(account))

    # Set a context boo if email/twitter should be shown, it is only shown
    # to administrators and to owner (account is same as context account)
    show_info = (current_user and current_user.admin) or \
                (current_user == profile)

    # ..or if the user has chosen to make it public
    show_email = show_info or profile.public_email
    show_twitter = show_info or profile.public_twitter
    profile_datasets = Dataset.all_by_account(current_user)
    cond = Dataset.managers.any(Account.id == profile.id)
    profile_datasets = profile_datasets.filter(cond)
    profile_datasets = Pager(profile_datasets, account=account, limit=15)
    return render_template('account/profile.html', profile=profile,
                           show_email=show_email, show_twitter=show_twitter,
                           profile_datasets=profile_datasets)
