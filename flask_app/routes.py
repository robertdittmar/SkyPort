# 3rd-party packages
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    Blueprint,
    session,
    g,
)
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

# stdlib
from datetime import datetime
import io
import base64

# local
from . import bcrypt
from . import mail
from . import slizer
from .forms import (
    SearchForm,
    MovieReviewForm,
    RegistrationForm,
    LoginForm,
    UpdateUsernameForm,
)
from .models import User, Post, load_user
from .utils import current_time


main = Blueprint("main", __name__)


""" ************ View functions ************ """


@main.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.account"))
    
    return render_template("index.html")


@main.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    if current_user.confirmed:
        try:
            results = movie_client.search(query)
        except ValueError as e:
            flash(str(e))
            return redirect(url_for("main.index"))

        return render_template("query.html", results=results)
    else:
        return render_template("not_confirmed.html", name=current_user.username, email=current_user.email)



@main.route("/user/<username>")
def user_detail(username):
    if current_user.confirmed:
        user = User.objects(username=username).first()
        reviews = Review.objects(commenter=user)

        return render_template("user_detail.html", username=username, reviews=reviews)
    else:
        return render_template("not_confirmed.html", name=current_user.username, email=current_user.email)


""" ************ User Management views ************ """


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        token = slizer.dumps(form.email.data)
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed, confirmed=False)
        user.save()
        
        msg = Message("Thank You For Joining SkyPort!", 
                      sender=("SkyPort", "skyportapp@gmail.com"), 
                      recipients=[form.email.data])
        link = url_for('main.confirm_email', token=token, _external=True)
        msg.body = "Hello and welcome to SkyPort! Please confirm your email at this link: {}".format(link)
        mail.send(msg)

        return redirect(url_for("main.login"))

    return render_template("register.html", title="Register", form=form)

@main.route('/confirm_email/<token>')
def confirm_email(token):
    message = "Thank you! Your email has been confirmed."
    email = slizer.loads(token)
    user = User.objects(email=email).first()
    user.modify(confirmed=True)
    
    return render_template("confirm_email.html", message=message)

@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            return redirect(url_for("main.index"))
        else:
            flash("Login failed. Check your username and/or password")
            return redirect(url_for("main.login"))

    return render_template("login.html", title="Login", form=form)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@main.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if current_user.confirmed:
        return render_template("account.html")
    else:
        return render_template("not_confirmed.html", name=current_user.username, email=current_user.email)
