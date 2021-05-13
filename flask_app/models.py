from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from .utils import current_time
import base64


@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    confirmed = db.BooleanField(required=True, default=False)

    # Returns unique string identifying our object
    def get_id(self):
        return self.username


class Post(db.Document):
    poster = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    title = db.StringField(required=True, min_length=1, max_length=100)

class StellarObject(db.Document):
    object_name = db.StringField(required=True, unique=True, min_length=1, max_length=100)
    
class Comment(db.Document):
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=1, max_length=1000)
    date = db.StringField(required=True)
    object_name = db.StringField(required=True, min_length=1, max_length=100)

class PostComment(db.Document):
    commenter = db.ReferenceField(User, required=True)
    poster = db.ReferenceField(User, required=True)
    post = db.ReferenceField(Post, required=True)
    content = db.StringField(required=True, min_length=1, max_length=1000)
    date = db.StringField(required=True)
    
    
    