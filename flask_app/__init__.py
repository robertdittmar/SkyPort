# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeSerializer
from werkzeug.utils import secure_filename
from flask_talisman import Talisman

# stdlib
from datetime import datetime
import os

# local
from .client import MovieClient


db = MongoEngine()
login_manager = LoginManager()
mail = Mail()
slizer = URLSafeSerializer('verysecret')
bcrypt = Bcrypt()
# from .users.routes import users
# from .movies.routes import movies
from .users.routes import users
from .stellar_objects.routes import stellar_objects


def page_not_found(e):
    return render_template("404.html"), 404

app = Flask(__name__)
UPLOAD_FOLDER = '/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["MONGODB_HOST"] = os.getenv("MONGODB_HOST")

    
app.config.from_pyfile("config.py", silent=False)
if test_config is not None:
    app.config.update(test_config)

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '1e6f73a05278e3'
app.config['MAIL_PASSWORD'] = 'ad88317303ff28'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)
bcrypt.init_app(app)
    
csp = {
        'default-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'stackpath.bootstrapcdn.com',
            'code.jquery.com',
            'cdn.jsdelivr.net'
            ],
        'img-src': '* data:'
}

Talisman(app, content_security_policy=csp)

app.register_blueprint(users)
app.register_blueprint(stellar_objects)
app.register_error_handler(404, page_not_found)

login_manager.login_view = "users.login"
