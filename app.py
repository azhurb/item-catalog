from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash, abort
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from models import Base, Category, CategoryItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps
import sys

if sys.version_info[0] == 3:
    xrange = range

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(func):
    """
    Check if user is logged in.
    """
    @wraps(func)
    def wrapper(**kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin'))
        else:
            func(**kwargs)
    return wrapper


def access_granted(func):
    """
    Check if the user has permission for the operation.
    """
    @wraps(func)
    def wrapper(**kwargs):
        if item.user_id != login_session['user_id']:
            flash("You are not authorized to change this entity.")
            return redirect(url_for('showCategories'))
        else:
            func(**kwargs)
    return wrapper


@app.route('/login')
def showLogin():
    """
    Show login page with anti-forgery state token.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    Gathers data from Google Sign In API and places it inside a
    session variable.
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """
    Only disconnect a connected google user.
    """
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400)
        )
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnect')
def disconnect():
    """
    Only disconnect a connected user.
    """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


@app.route('/')
@app.route('/catalog/')
def showCategories():
    """
    Show all categories.
    """
    categories = session.query(Category).order_by(asc(Category.name))
    if request_wants_json():
        return jsonify(Category=[x.serialize for x in categories])
    else:
        latest_items = (session.query(CategoryItem)
                        .order_by(desc(CategoryItem.id)).limit(10))
        return render_template('categories.html',
                               categories=categories,
                               latest_items=latest_items)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():
    """
    Create a new category.
    """
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


@app.route('/catalog/<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    """
    Edit a category.
    """
    editedCategory = session.query(
        Category).filter_by(id=category_id).one_or_none()

    if editedCategory is None:
        return abort(404)

    if editedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized "
        "to edit this category. Please create your own category in order to "
        "edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=editedCategory)


@app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    """
    Delete a category.
    """
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one_or_none()

    if categoryToDelete is None:
        return abort(404)

    if categoryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized "
        "to delete this category. Please create your own category in order "
        "to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategories', category_id=category_id))
    else:
        return render_template('deleteCategory.html',
                               category=categoryToDelete)


@app.route('/catalog/<int:category_id>/')
@app.route('/catalog/<int:category_id>/items/')
def showCategory(category_id):
    """
    Show a category.
    """
    category = session.query(
        Category).filter_by(id=category_id).one_or_none()

    if category is None:
        return abort(404)

    creator = getUserInfo(category.user_id)
    items = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    if request_wants_json():
        return jsonify(Item=[x.serialize for x in items])
    else:
        return render_template('category.html', items=items,
                               category=category, creator=creator)


@app.route('/catalog/<int:category_id>/items/new/', methods=['GET', 'POST'])
@login_required
def newCategoryItem(category_id):
    """
    Create a new category item.
    """
    category = session.query(
        Category).filter_by(id=category_id).one_or_none()

    if category is None:
        return abort(404)

    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized "
        "to add menu items to this category. Please create your own category "
        "in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newItem = CategoryItem(name=request.form['name'],
                               description=request.form['description'],
                               category_id=category_id,
                               user_id=category.user_id)
        session.add(newItem)
        session.commit()
        flash('New Item "%s" Successfully Created' % (newItem.name))
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('newcategoryitem.html', category_id=category_id)


@app.route('/catalog/<int:category_id>/items/<int:item_id>/', methods=['GET'])
def showCategoryItem(category_id, item_id):
    """
    Show a category item.
    """
    item = session.query(CategoryItem).filter_by(id=item_id).one_or_none()
    category = session.query(Category).filter_by(id=category_id).one_or_none()

    if category is None or item is None:
        return abort(404)

    if request_wants_json():
        return jsonify(Item=item.serialize)
    else:
        return render_template('viewCategoryItem.html', category=category,
                               item=item)


@app.route('/catalog/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editCategoryItem(category_id, item_id):
    """
    Edit a category item.
    """
    editedItem = session.query(
        CategoryItem).filter_by(id=item_id).one_or_none()
    category = session.query(
        Category).filter_by(id=category_id).one_or_none()

    if category is None or editedItem is None:
        return abort(404)

    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized "
        "to edit items in this category. Please create your own category in "
        "order to edit items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Category Item Successfully Edited')
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('editCategoryItem.html',
                               category_id=category_id,
                               item_id=item_id, item=editedItem)


@app.route('/catalog/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteCategoryItem(category_id, item_id):
    """
    Delete a category item.
    """
    category = session.query(
        Category).filter_by(id=category_id).one_or_none()
    itemToDelete = session.query(
        CategoryItem).filter_by(id=item_id).one_or_none()

    if category is None or itemToDelete is None:
        return abort(404)

    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() {alert('You are not authorized "
        "to delete items from this category. Please create your own category "
        "in order to delete items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Category Item Successfully Deleted')
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('deleteCategoryItem.html', item=itemToDelete)


# Helpers
def getUserID(email):
    """
    Get user ID by email.
    """
    try:
        user = session.query(User).filter_by(email=email).one_or_none()
        if user is None:
            return None
        return user.id
    except:
        return None


def createUser(login_session):
    """
    Add new user to the database.
    """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
    Get user info by user ID.
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def request_wants_json():
    """
    Check if JSON requested.
    """
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
