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
import os
import base64
import uuid

# local
from .. import bcrypt
from .. import mail
from .. import slizer
from ..forms import (
    SearchForm,
    PostForm,
    CommentForm,
    RegistrationForm,
    LoginForm
)
from ..models import User, Post, PostComment, load_user
from ..utils import current_time


users = Blueprint("users", __name__)

@users.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))
    
    return render_template("index.html")

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        token = slizer.dumps(form.email.data)
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed, confirmed=False)
        user.save()
        
        msg = Message("Thank You For Joining SkyPort!", 
                      sender=("SkyPort", "skyportapp@gmail.com"), 
                      recipients=[form.email.data])
        link = url_for('users.confirm_email', token=token, _external=True)
        msg.body = "Hello and welcome to SkyPort! Please confirm your email at this link: \n{}".format(link)
        mail.send(msg)

        return redirect(url_for("users.login"))

    return render_template("register.html", title="Register", form=form)

@users.route('/confirm_email/<token>')
def confirm_email(token):
    message = "Thank you! Your email has been confirmed."
    email = slizer.loads(token)
    user = User.objects(email=email).first()
    user.modify(confirmed=True)
    
    return render_template("confirm_email.html", message=message)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            return redirect(url_for("users.index"))
        else:
            flash("Login failed. Check your username and/or password")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login", form=form)

@users.route("/post", methods=["GET", "POST"])
@login_required
def post():
    print("called post!")
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            poster=current_user._get_current_object(),
            content=form.content.data,
            date=current_time(),
            title=form.title.data
        )
        post.save()
        return redirect(url_for("users.account"))
    
    return render_template("post.html", form=form)

@users.route("/post_detail/<user>/<date>", methods={"GET", "POST"})
@login_required
def post_detail(user, date):
    get_post = Post.objects(date=date)
    valid_posts = []
    for p in get_post:
        if p.poster.username == user:
            valid_posts.append(p)
            
    comments = PostComment.objects(post=valid_posts[0])
    form = CommentForm()
    if form.validate_on_submit():
        post_comment = PostComment(
            commenter=current_user._get_current_object(),
            poster=valid_posts[0].poster,
            post=valid_posts[0],
            content=form.content.data,
            date=current_time()
        )
        post_comment.save()
        return redirect(url_for("users.post_detail", user=valid_posts[0].poster.username, date=date))
    
    return render_template("post_detail.html", post=valid_posts[0], comments=comments, form=form)

@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("users.index"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if current_user.confirmed:
        return render_template("account.html")
    else:
        return render_template("not_confirmed.html", name=current_user.username, email=current_user.email)
