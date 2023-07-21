import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from dotenv import load_dotenv
from models import db, connect_db, User, Post, UserCard, WantCard
from forms import LoginForm, SignUpForm, PostForm
from pokemontcgsdk import Card, Set, Type, Subtype, Supertype, Rarity, RestClient
import urllib.request
import json
import urllib.parse

CURR_USER_KEY = "curr_user"

load_dotenv(override=True)
pw = os.getenv("pw")
api_pw = os.getenv("api_pw")

RestClient.configure(api_pw)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{pw}@localhost/pokemon'


app.app_context().push()

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route("/login", methods=["GET", "POST"])
def sign_in():
    """user sign in form"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route("/")
def home_page():
    """ home directory"""
    # cards = Card.where(q='set.name:generations supertype:pokemon')
    set = Set.where(orderBy="releaseDate")

    new_set = set[::-1]
    newest_series = new_set[0].series
    cards = Card.where(
        q=f'set.series:"{newest_series}"', orderBy="-tcgplayer.prices.holofoil.mid", page=1, pageSize=9)

    exp_cards = Card.where(
        orderBy="-tcgplayer.prices.holofoil.mid", page=1, pageSize=9)
    return render_template('index.html', cards=cards, exp_cards=exp_cards)
