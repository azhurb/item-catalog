from flask import Flask, render_template

from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)

from app.mod_auth.controllers import mod_auth as auth_module

app.register_blueprint(auth_module)

db.create_all()
