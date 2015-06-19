import colander
import logging

from flask import Blueprint, render_template, request, redirect
from flask.ext.login import current_user, login_user
from flask.ext.babel import gettext as _
from sqlalchemy.sql.expression import or_
from werkzeug.security import generate_password_hash
from apikit import obj_or_404, Pager, jsonify

from spendb.core import db, url_for
from spendb.auth import require
from spendb.model import Account, Dataset
from spendb.validation.account import AccountRegister, AccountSettings
from spendb.lib.mailer import send_reset_link
from spendb.lib.helpers import flash_error, flash_success
from spendb.views.cache import disable_cache


log = logging.getLogger(__name__)
blueprint = Blueprint('account_api', __name__)


@blueprint.route('/register', methods=['POST', 'PUT'])
def register():
    """ Perform registration of a new user """
    disable_cache()
    require.account.create()
    errors, values = {}, dict(request.form.items())

    try:
        # Grab the actual data and validate it
        data = AccountRegister().deserialize(values)

        # Check if the username already exists, return an error if so
        if Account.by_name(data['name']):
            raise colander.Invalid(
                AccountRegister.name,
                _("Login name already exists, please choose a "
                  "different one"))

        # Check if passwords match, return error if not
        if not data['password1'] == data['password2']:
            raise colander.Invalid(AccountRegister.password1,
                                   _("Passwords don't match!"))

        # Create the account
        account = Account()
        account.name = data['name']
        account.fullname = data['fullname']
        account.email = data['email']
        account.public_email = data['public_email']
        account.password = generate_password_hash(data['password1'])

        db.session.add(account)
        db.session.commit()

        # Perform a login for the user
        login_user(account, remember=True)

        # Registration successful - Redirect to the front page
        return redirect(url_for('home.index'))
    except colander.Invalid as i:
        errors = i.asdict()
    return render_template('account/login.html', form_fill=values,
                           form_errors=errors)


@blueprint.route('/settings')
def settings():
    """ Change settings for the logged in user """
    disable_cache()
    require.account.update(current_user)
    values = current_user.to_dict()
    if current_user.public_email:
        values['public_email'] = current_user.public_email
    if current_user.public_twitter:
        values['public_twitter'] = current_user.public_twitter
    values['api_key'] = current_user.api_key
    return render_template('account/settings.html',
                           form_fill=values)


@blueprint.route('/settings', methods=['POST', 'PUT'])
def settings_save():
    """ Change settings for the logged in user """
    require.account.update(current_user)
    errors, values = {}, dict(request.form.items())

    try:
        data = AccountSettings().deserialize(values)

        # If the passwords don't match we notify the user
        if not data['password1'] == data['password2']:
            raise colander.Invalid(AccountSettings.password1,
                                   _("Passwords don't match!"))

        current_user.fullname = data['fullname']
        current_user.email = data['email']
        current_user.public_email = data['public_email']
        if data['twitter'] is not None:
            current_user.twitter_handle = data['twitter'].lstrip('@')
            current_user.public_twitter = data['public_twitter']

        # If a new password was provided we update it as well
        if data['password1'] is not None and len(data['password1']):
            current_user.password = generate_password_hash(
                data['password1'])

        # Do the actual update in the database
        db.session.add(current_user)
        db.session.commit()

        # Let the user know we've updated successfully
        flash_success(_("Your settings have been updated."))
    except colander.Invalid as i:
        # Load errors if we get here
        errors = i.asdict()

    return render_template('account/settings.html',
                           form_fill=values,
                           form_errors=errors)


@blueprint.route('/dashboard')
def dashboard(format='html'):
    """
    Show the user profile for the logged in user
    """
    disable_cache()
    require.account.logged_in()
    return profile(current_user.name)


@blueprint.route('/accounts/_complete')
def complete(format='json'):
    disable_cache()
    if not current_user.is_authenticated():
        msg = _("You are not authorized to see that page")
        return jsonify({'errors': msg}, status=403)

    query = db.session.query(Account)
    filter_string = request.args.get('q', '') + '%'
    query = query.filter(or_(Account.name.ilike(filter_string),
                             Account.fullname.ilike(filter_string)))
    return jsonify(Pager(query))


@blueprint.route('/account/forgotten', methods=['POST', 'GET'])
def trigger_reset():
    """
    Allow user to trigger a reset of the password in case they forget it
    """
    disable_cache()
    # If it's a simple GET method we return the form
    if request.method == 'GET':
        return render_template('account/trigger_reset.html')

    # Get the email
    email = request.form.get('email')

    # Simple check to see if the email was provided. Flash error if not
    if email is None or not len(email):
        flash_error(_("Please enter an email address!"))
        return render_template('account/trigger_reset.html')

    # Get the account for this email
    account = Account.by_email(email)

    # If no account is found we let the user know that it's not registered
    if account is None:
        flash_error(_("No user is registered under this address!"))
        return render_template('account/trigger_reset.html')

    # Send the reset link to the email of this account
    send_reset_link(account)

    # Let the user know that email with link has been sent
    flash_success(_("You've received an email with a link to reset your "
                    "password. Please check your inbox."))

    # Redirect to the login page
    return redirect(url_for('account.login'))


@blueprint.route('/account/reset')
def do_reset():
    email = request.args.get('email')
    if email is None or not len(email):
        flash_error(_("The reset link is invalid!"))
        return redirect(url_for('account.login'))

    account = Account.by_email(email)
    if account is None:
        flash_error(_("No user is registered under this address!"))
        return redirect(url_for('account.login'))

    if request.args.get('token') != account.token:
        flash_error(_("The reset link is invalid!"))
        return redirect(url_for('account.login'))

    login_user(account)
    flash_success(
        _("Thanks! You have now been signed in - please change "
          "your password!"))
    return redirect(url_for('account.settings'))


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
