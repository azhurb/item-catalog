from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

from app import db

from app.mod_auth.models import User

mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

@mod_auth.route('/login/', methods=['GET', 'POST'])
    """
    Show login page with anti-forgery state token.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)