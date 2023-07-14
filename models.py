from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    country = db.Column(db.Text)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())


class Post(db.Model):
    """Post."""

    __tablename_ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.utcnow())
    country = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    card_id = db.Column(db.Text, nullable=False)

    user = db.relationship("User")


class UserCard(db.Model):
    """Cards owned by user"""

    __tablename__ = "card_owned"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)


class WantCard(db.Model):
    """Cards user want"""

    __tablename__ = "card_wanted"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
