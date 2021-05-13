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
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_mongoengine import MongoEngine
from flask_login import current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

# stdlib
from datetime import datetime
import io
import base64

# local
from .. import bcrypt
from ..forms import (SearchForm, PostForm, AddObjectForm, CommentForm)
from ..models import User, Post, StellarObject, Comment
from ..utils import current_time


stellar_objects = Blueprint("stellar_objects", __name__)

@stellar_objects.route("/search", methods=["GET", "POST"])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for("stellar_objects.query_results", query=form.query.data))
    
    return render_template("search.html", form=form)

@stellar_objects.route("/search-results/<query>", methods=["GET", "POST"])
@login_required
def query_results(query):
    stel_obj = StellarObject.objects(object_name__icontains=query)
    posts = Post.objects(title__icontains=query)
    users = User.objects(username__icontains=query)
    return render_template("stellar_object_list.html", stel_obj=stel_obj, posts=posts, users=users, query=query)

@stellar_objects.route("/request_object", methods=["GET", "POST"])
@login_required
def add_object():
    form = AddObjectForm()
    if form.validate_on_submit():
        stel_obj = StellarObject(object_name=form.name.data)
        stel_obj.save()
        
        stel = StellarObject.objects(object_name=form.name.data)
        
        return redirect(url_for("stellar_objects.stellar_object", stellar_object=stel.first().object_name))
        
    return render_template("add_object.html", form=form)
    

@stellar_objects.route("/stellar_object/<stellar_object>", methods=["GET", "POST"])
@login_required
def stellar_object(stellar_object):
    stel = StellarObject.objects(object_name__iexact=stellar_object).first()
    comments = Comment.objects(object_name__iexact=stellar_object)
    
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            commenter=current_user._get_current_object(),
            content=form.content.data,
            date=current_time(),
            object_name=stellar_object
        )
        comment.save()
        comments = Comment.objects(object_name=stellar_object)
        return redirect(url_for("stellar_objects.stellar_object", stellar_object=stellar_object))
    
    return render_template("stellar_object.html", stel=stel, comments=comments, form=form)

@stellar_objects.route("/user/<username>")
@login_required
def user_detail(username):
    user = User.objects(username=username).first()
    posts = Post.objects(poster=user)
    comments = Comment.objects(commenter=user)

    return render_template("user_detail.html", username=username, posts=posts, comments=comments)

@stellar_objects.route("/about")
def about():
    return render_template("about.html")
