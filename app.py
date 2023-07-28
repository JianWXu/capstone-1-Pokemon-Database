import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from dotenv import load_dotenv
from models import db, connect_db, User, Post, UserCard, WantCard
from forms import LoginForm, SignUpForm, PostForm, EditPost, SearchPokemon
from pokemontcgsdk import Card, Set, Type, Subtype, Supertype, Rarity, RestClient
import urllib.request
import json
import urllib.parse
from sqlalchemy.exc import IntegrityError

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
    searchForm = SearchPokemon()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form, searchForm=searchForm)


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    """user sign up for new account"""

    form = SignUpForm()
    searchForm = SearchPokemon()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                country=form.country.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form, searchForm=searchForm)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form, searchForm=searchForm)


@app.route("/logout")
def log_out():

    do_logout()
    flash("Logged out", category="success")
    return redirect("/login")


###########################################################################
# home directory

@app.route("/")
def home_page():
    # cards = Card.where(q='set.name:generations supertype:pokemon')
    energies = Type.all()
    searchForm = SearchPokemon()
    set = Set.where(orderBy="releaseDate")
    user = g.user
    new_set = set[::-1]
    newest_series = new_set[0].series
    cards = Card.where(
        q=f'set.series:"{newest_series}"', orderBy="-tcgplayer.prices.holofoil.mid", page=1, pageSize=9)
    
    exp_cards = Card.where(
        orderBy="-tcgplayer.prices.holofoil.mid", page=1, pageSize=9)
    return render_template('index.html', cards=cards, exp_cards=exp_cards, energies=energies, user=user, searchForm=searchForm)


##########################################################################
# energy card pages


@app.route("/<energy>")
def colorless_page(energy):
    user = g.user
    energies = Type.all()
    searchForm = SearchPokemon()

    cards = Card.where(
        q=f'types:"{energy}"', orderBy="-set.releaseDate", page=1, pageSize=9)
    return render_template('/cards/energies.html', energy=energy, energies=energies, cards=cards, user=user, searchForm=searchForm)


#######################################################################
# search card page

@app.route("/search", methods=["GET", "POST"])
def search_page():

    user = g.user
    energies = Type.all()
    searchForm = SearchPokemon()
    if request.method == "POST":
        if searchForm.validate_on_submit():
            pokemon_search = searchForm.pokemon.data
            pokemons = Card.where(
                q=f'name:"{pokemon_search}"', page=1, pageSize=24)
            return render_template('/cards/search_page.html', user=user, energies=energies, pokemons=pokemons, searchForm=searchForm)
    return render_template('/', user=user, energies=energies, searchForm=searchForm, pokemons=pokemons)


#######################################################################
# each card pages

@app.route("/cards/<card_id>")
def each_card(card_id):

    # if not g.user:
    #     flash("Access unauthorized.", "danger")
    #     return render_template('each_card.html', )
    user = g.user
    energies = Type.all()
    searchForm = SearchPokemon()

    card = Card.find(card_id)

    if not g.user:

        return render_template('/cards/each_card.html', card=card, searchForm=searchForm)

    card_owned_list = [c.card_id for c in g.user.card_owned]

    card_wanted_list = [c.card_id for c in g.user.card_wanted]

    return render_template('/cards/each_card.html', card=card, energies=energies, card_owned_list=card_owned_list, card_wanted_list=card_wanted_list, user=user, searchForm=searchForm)


######################################################################
# add card to user wanted model

@app.route("/user/cards/wanted/<card_id>", methods=["POST"])
def want_card(card_id):

    user_id = g.user.id
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get(user_id)

    new_wanted = WantCard(
        card_id=card_id,
        user_id=user_id
    )
    db.session.add(new_wanted)
    db.session.commit()

    return redirect(f"/cards/{card_id}")

######################################################################
# add card to user owned model


@app.route("/user/cards/owned/<card_id>", methods=["POST"])
def owned_card(card_id):

    user_id = g.user.id
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get(user_id)

    new_owned = UserCard(
        card_id=card_id,
        user_id=user_id
    )
    db.session.add(new_owned)
    db.session.commit()

    return redirect(f"/cards/{card_id}")


######################################################################
# delete card from user owned model

@app.route("/user/cards/owned/<card_id>/delete", methods=["POST"])
def delete_ownedCard(card_id):

    user_id = g.user.id

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    ownedCard_id = UserCard.query.filter_by(
        card_id=card_id, user_id=user_id).first()

    db.session.delete(ownedCard_id)
    db.session.commit()
    return redirect(f"/cards/{card_id}")


######################################################################
# delete card from user wanted model

@app.route("/user/cards/wanted/<card_id>/delete", methods=["POST"])
def delete_wantedCard(card_id):

    user_id = g.user.id

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    wantedCard_id = WantCard.query.filter_by(
        card_id=card_id, user_id=user_id).first()
    db.session.delete(wantedCard_id)
    db.session.commit()
    return redirect(f"/cards/{card_id}")


######################################################################
# user profile

@app.route("/user/<int:user_id>")
def user_profile(user_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")

    user = g.user
    user_id = user.id
    energies = Type.all()
    searchForm = SearchPokemon()

    card_api_list = []

    owned_cards = UserCard.query.filter_by(user_id=user_id).all()
    for card in owned_cards:
        card_api_list.append(Card.find(card.card_id))

    want_api_list = []

    wanted_cards = WantCard.query.filter_by(user_id=user_id).all()
    for card in wanted_cards:
        want_api_list.append(Card.find(card.card_id))

    self_posts = Post.query.filter_by(user_id=user_id).all()

    return render_template("users/profile.html", user=user, user_id=user_id, owned_cards=owned_cards, card_api_list=card_api_list, want_api_list=want_api_list, self_posts=self_posts, energies=energies, searchForm=searchForm)


######################################################################
# making a post

@app.route("/posts/new", methods=["GET", "POST"])
def new_post():

    user = g.user
    energies = Type.all()

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")

    user_id = g.user.id

    form = PostForm()
    searchForm = SearchPokemon()
    if request.method == "POST":

        if form.validate_on_submit():
            file = request.files['file']
            post = Post(title=form.title.data, content=form.content.data,
                        user_id=user_id, country=form.country.data, filename=file.filename, data=file.read())
            db.session.add(post)
            db.session.commit()
            
            return redirect(f"/user/{g.user.id}")

    return render_template('posts/new_post.html', user=user, form=form, energies=energies, searchForm=searchForm)


######################################################################
# editing a post

@app.route("/posts/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):

    user = g.user
    energies = Type.all()
    post = Post.query.get(post_id)

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")

    user_id = g.user.id

    form = EditPost()
    searchForm = SearchPokemon()

    if form.validate_on_submit():

        post.title = form.title.data
        post.content = form.content.data
        post.country = form.country.data

        db.session.commit()

        return redirect(f'/user/{user_id}')

    return render_template('posts/edit_post.html', user=user, form=form, energies=energies, post=post, searchForm=searchForm)


######################################################################
# deleting a post

@app.route('/posts/delete/<int:post_id>', methods=["POST"])
def messages_destroy(post_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()

    return redirect(f"/user/{g.user.id}")
