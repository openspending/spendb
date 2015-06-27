import colander
import logging

from flask import Blueprint, request, redirect
from flask.ext.login import current_user, login_user
from flask.ext.babel import gettext as _
from sqlalchemy.sql.expression import or_
from werkzeug.security import generate_password_hash
from apikit import obj_or_404, Pager, jsonify, request_data

from spendb.core import db
from spendb.auth import require
from spendb.model import Account
from spendb.validation.account import AccountRegister, AccountSettings
from spendb.lib.mailer import send_reset_link


log = logging.getLogger(__name__)
blueprint = Blueprint('account_api', __name__)


@blueprint.route('/accounts', methods=['POST', 'PUT'])
def register():
    """ Perform registration of a new user """
    require.account.create()
    data = AccountRegister().deserialize(request_data())

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
    return jsonify(account)


@blueprint.route('/accounts/<account>', methods=['POST', 'PUT'])
def update(account):
    """ Change settings for the logged in user """
    require.account.update(current_user)
    data = AccountSettings().deserialize(request_data())

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
    return jsonify(current_user)


@blueprint.route('/accounts/_complete')
def complete(format='json'):
    if not current_user.is_authenticated():
        msg = _("You are not authorized to see that page")
        return jsonify({'status': 'error', 'message': msg}, status=403)

    query = db.session.query(Account)
    filter_string = request.args.get('q', '') + '%'
    query = query.filter(or_(Account.name.ilike(filter_string),
                             Account.fullname.ilike(filter_string)))
    return jsonify(Pager(query))


@blueprint.route('/reset', methods=['GET'])
def do_reset():
    email = request.args.get('email')
    if email is None or not len(email):
        # flash_error(_("The reset link is invalid!"))
        return redirect('/login')

    account = Account.by_email(email)
    if account is None:
        # flash_error(_("No user is registered under this address!"))
        return redirect('/login')

    if request.args.get('token') != account.token:
        # flash_error(_("The reset link is invalid!"))
        return redirect('/login')

    login_user(account)
    # flash_success(
    #     _("Thanks! You have now been signed in - please change "
    #       "your password!"))
    return redirect('/settings')


@blueprint.route('/reset', methods=['POST'])
def trigger_reset():
    """
    Allow user to trigger a reset of the password in case they forget it
    """
    email = request_data().get('email')

    # Simple check to see if the email was provided. Flash error if not
    if email is None or not len(email):
        return jsonify({
            'status': 'error',
            'message': _("Please enter an email address!")
        }, status=400)

    account = Account.by_email(email)

    # If no account is found we let the user know that it's not registered
    if account is None:
        return jsonify({
            'status': 'error',
            'message': _("No user is registered under this address!")
        }, status=400)

    # Send the reset link to the email of this account
    send_reset_link(account)
    return jsonify({
        'status': 'ok',
        'message': _("You've received an email with a link to reset your "
                     "password. Please check your inbox.")
    })


@blueprint.route('/accounts/<account>')
def view(account):
    """ Generate a profile page for a user (from the provided name) """
    account = obj_or_404(Account.by_name(account))
    data = account.to_dict()
    if account == current_user or current_user.admin:
        data['email'] = account.email
        data['public_email'] = account.public_email
        data['twitter_handle'] = account.twitter_handle
        data['public_twitter'] = account.public_twitter
    return jsonify(data)
