import os

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from dotenv import load_dotenv
from models import db, connect_db, User, Post, UserCard, WantCard
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
# url = 'https://api.pokemontcg.io/v2/cards'


app.app_context().push()

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route("/")
def home_page():
    # cards = Card.where(q='set.name:generations supertype:pokemon')
    set = Set.where(orderBy="releaseDate")

    new_set = set[::-1]
    newest_series = new_set[0].series
    cards = Card.where(
        q=f'set.series:"{newest_series}"', orderBy="-tcgplayer.prices.holofoil.mid", page=1, pageSize=9)

    exp_cards = Card.where(
        orderBy="-tcgplayer.prices.holofoil.mid", page=1, pageSize=9)
    return render_template('index.html', cards=cards, exp_cards=exp_cards)
