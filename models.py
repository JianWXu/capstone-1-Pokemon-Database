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

    posts = db.relationship('Post', backref="user_post")

    card_wanted = db.relationship(
        'WantCard', backref="user_want", lazy='dynamic')
    card_owned = db.relationship(
        'UserCard', backref="user_owned", lazy='dynamic')

    @classmethod
    def signup(cls, username, email, password, country):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            country=country
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


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


class UserCard(db.Model):
    """Cards owned by user"""

    __tablename__ = "card_owned"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)

    # user = db.relationship("User")


class WantCard(db.Model):
    """Cards user want"""

    __tablename__ = "card_wanted"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)


def connect_db(app):

    db.app = app
    db.init_app(app)
