from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    pass

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    pass

@app.route('/fbdisconnect')
def fbdisconnect():
    pass

@app.route('/gconnect', methods=['POST'])
def gconnect():
    pass

@app.route('/gdisconnect')
def gdisconnect():
    pass

# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCategories():
    pass

# Create a new category
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():
    pass

# Edit a category
@app.route('/catalog/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    pass

# Delete a category
@app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    pass

# Show a category
@app.route('/catalog/<int:category_id>/')
@app.route('/catalog/<int:category_id>/items/')
def showCategory(category_id):
    pass

# Create a new category item
@app.route('/catalog/<int:category_id>/items/new/', methods=['GET', 'POST'])
def newCategoryItem(category_id):
    pass

# Edit a category item
@app.route('/catalog/<int:category_id>/items/<int:item_id>/edit', methods=['GET', 'POST'])
def editCategoryItem(category_id, item_id):
    pass

# Delete a category item
@app.route('//catalog/<int:category_id>/items/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteCategoryItem(category_id, item_id):
    pass

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    pass

# TODO: Add API routes

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
