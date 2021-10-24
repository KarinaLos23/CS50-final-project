from functools import wraps, lru_cache
from tempfile import mkdtemp

from flask import Flask, redirect, render_template, request, session, jsonify, flash
from flask_session import Session
from pip._vendor import requests
from werkzeug.security import check_password_hash, generate_password_hash

import metadata
from metadata import insert, get_movies_from_wishlist, get_movies_from_watchlist, get_movies_from_favourites, \
    get_person_by_id, get_friends, get_feed, get_posts, get_movies_by_title, remove_watchlist_item, \
    make_watched, remove_wishlist_item, remove_favourites_item, create_review, get_people, get_favourites, \
    has_watchlist, has_friendship, has_review, has_wishlist, has_favourites, get_stats, get_photo, has_marked_as_useful, \
    add_useful_badge, get_friends_wishes, get_persons_useful

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


@app.route('/', methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("email"):
            return apology("must provide email", 403)
        elif not request.form.get("pwd"):
            return apology("must provide password", 403)

        username = request.form.get("email")
        user = metadata.get_user(username)
        if user is None or not check_password_hash(user.password_hash, request.form.get("pwd")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = user.id
        return redirect("/home")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("name"):
            return apology("must provide first name", 403)
        elif not request.form.get("surname"):
            return apology("must provide surname", 403)
        elif not request.form.get("email"):
            return apology("must provide e-mail", 403)
        elif not request.form.get("pwd"):
            return apology("must provide password", 403)
        elif not request.form.get("pwdconf"):
            return apology("must confirm password", 403)

        if request.form.get("pwd") != request.form.get("pwdconf"):
            return apology("passwords must match", 403)

        username = request.form.get("email")
        user = metadata.get_user(username)
        if user is not None:
            return apology("username already exists", 403)

        hash_val = generate_password_hash(request.form.get("pwd"))
        new_user = metadata.Users(email=request.form.get("email"), name=request.form.get("name"),
                                  surname=request.form.get("surname"), password_hash=hash_val)
        insert(new_user)
        return redirect("/")
    else:
        return render_template("register.html")


@app.route('/home')
@login_required
def home():
    user_id = session["user_id"]
    friends = get_friends(user_id)
    feed = get_feed(user_id)
    useful = {u.review_id for u in get_persons_useful(session["user_id"])}
    return render_template("home.html", friends=friends, feed=feed, useful=useful)


@app.route('/find_movies', methods=["POST"])
@login_required
def find_movies():
    id = session["user_id"]
    movies = get_movies_by_title(request.json)
    poster_paths = {m.id: get_poster_path(m.id) for m in movies}
    # initializing set made up from movie ids:
    watch = {m.id for m in get_movies_from_watchlist(id)}
    wish = {m.id for m in get_movies_from_wishlist(id)}
    movies_to_return = [{"id": m.id, "title": m.title, "year": m.year, "watch": m.id in watch, "wish": m.id in wish,
                         "poster": poster_paths[m.id]} for m in movies]
    return jsonify(movies_to_return)


@app.route('/find_people', methods=["GET", "POST"])
@login_required
def find_people():
    person = request.get_json()
    people = get_people(person["name"], person["surname"], session["user_id"])
    friends = {f.id for f in get_friends(session["user_id"])}
    people_to_return = [{"id": p.id, "name": p.name, "surname": p.surname, "friend": p.id in friends} for p in people]
    for p in people_to_return:
        photo = get_photo(p["id"])
        p["img_data"] = photo.img_data if photo is not None else None
    return jsonify(people_to_return)


@app.route('/add_to_friends/<person_id>', methods=["POST"])
@login_required
def add_to_friends(person_id):
    if not has_friendship(session["user_id"], person_id):
        new_friendship = metadata.Friends(person_id=session["user_id"], friend_id=person_id)
        insert(new_friendship)
    return jsonify(success=True)


@app.route('/post_review/<movie_id>', methods=["POST"])
@login_required
def post_review(movie_id):
    if not has_review(movie_id, session["user_id"]):
        post = request.get_json()
        create_review(session["user_id"], movie_id, post["reviewText"], post["rating"])
    return jsonify(success=True)


@app.route('/watchlist', methods=["GET"])
@login_required
def my_watchlist():
    return watchlist(session["user_id"])


@app.route('/watchlist/<person_id>', methods=["GET"])
@login_required
def watchlist(person_id):
    movies = get_movies_from_watchlist(person_id)
    poster_paths = {m.id: get_poster_path(m.id) for m in movies}
    favourites_ids = {f.movie_id for f in get_favourites(person_id)}
    reviewed = {p["movie_id"] for p in get_posts(session["user_id"])}
    return render_template("watchlist.html", person_id=person_id, watchlist=movies, favourites_ids=favourites_ids,
                           reviewed=reviewed, poster_paths=poster_paths)


@lru_cache(maxsize=None)
def get_poster_path(movie_id):
    response = requests.get(
        "https://api.themoviedb.org/3/find/tt%07d?api_key=15d2ea6d0dc1d476efbca3eba2b9bbfb&external_source=imdb_id" % movie_id)
    try:
        return "http://image.tmdb.org/t/p/w200" + response.json()['movie_results'][0]['poster_path']
    except:
        return '/static/pics/default-poster.jpg'


@app.route('/add_to_watchlist/<movie_id>', methods=["POST"])
@login_required
def add_to_watchlist(movie_id):
    if not has_watchlist(movie_id, session["user_id"]):
        new_watchlist_element = metadata.Watchlist(person_id=session["user_id"], movie_id=movie_id)
        insert(new_watchlist_element)
    return jsonify(success=True)


@app.route('/wishlist/<person_id>', methods=["GET"])
@login_required
def wishlist(person_id):
    movies = get_movies_from_wishlist(person_id)
    poster_paths = {m.id: get_poster_path(m.id) for m in movies}
    fw = get_friends_wishes(person_id)
    return render_template("wishlist.html", person_id=person_id, wishlist=movies, fw=fw, poster_paths=poster_paths)


@app.route('/add_to_wishlist/<movie_id>', methods=["POST"])
@login_required
def add_to_wishlist(movie_id):
    if not has_wishlist(movie_id, session["user_id"]):
        new_wishlist_element = metadata.Wishlist(person_id=session["user_id"], movie_id=movie_id)
        insert(new_wishlist_element)
    return jsonify(success=True)


@app.route('/favourites/<person_id>', methods=["GET"])
@login_required
def favourites(person_id):
    movies = get_movies_from_favourites(person_id)
    poster_paths = {m.id: get_poster_path(m.id) for m in movies}
    return render_template("favourites.html", person_id=person_id, favourites=movies, poster_paths=poster_paths)


@app.route('/add_to_favourites/<movie_id>', methods=["POST"])
@login_required
def add_to_favourites(movie_id):
    if not has_favourites(movie_id, session["user_id"]):
        new_favourites_element = metadata.Favourites(person_id=session["user_id"], movie_id=movie_id)
        insert(new_favourites_element)
    return jsonify(success=True)


@app.route('/remove_from_watchlist/<movie_id>', methods=["POST"])
@login_required
def remove_from_watchlist(movie_id):
    remove_watchlist_item(movie_id, session["user_id"])
    return jsonify(success=True)


@app.route('/remove_from_wishlist/<movie_id>', methods=["POST"])
@login_required
def remove_from_wishlist(movie_id):
    remove_wishlist_item(movie_id, session["user_id"])
    return jsonify(success=True)


@app.route('/remove_from_favourites/<movie_id>', methods=["POST"])
@login_required
def remove_from_favourites(movie_id):
    remove_favourites_item(movie_id, session["user_id"])
    return jsonify(success=True)


@app.route('/transfer_to_watchlist/<movie_id>', methods=["POST"])
@login_required
def transfer_to_watchlist(movie_id):
    if not has_watchlist(movie_id, session["user_id"]):
        make_watched(movie_id, session["user_id"])
    return jsonify(success=True)


@app.route('/profile')
@login_required
def profile():
    person_id = session["user_id"]
    person = get_person_by_id(person_id)
    posts = get_posts(person_id)
    stats = get_stats(person_id)
    photo = get_photo(person_id)
    img_data = photo.img_data if photo is not None else None
    return render_template("profile.html", person=person, posts=posts, stats=stats, img_data=img_data)


@app.route('/friend/<friend_id>')
@login_required
def friend(friend_id):
    friend = get_person_by_id(friend_id)
    watchlist = get_movies_from_watchlist(friend_id)
    wishlist = get_movies_from_wishlist(friend_id)
    stats = get_stats(friend_id)
    posts = get_posts(friend_id)
    useful = {u.review_id for u in get_persons_useful(session["user_id"])}
    photo = get_photo(friend_id)
    img_data = photo.img_data if photo is not None else None
    return render_template("friend.html", friend=friend, watchlist=watchlist, wishlist=wishlist, posts=posts,
                           stats=stats, img_data=img_data, useful=useful)


@app.route('/friend_watchlist/<friend_id>')
@login_required
def friend_watchlist(friend_id):
    friend = get_person_by_id(friend_id)
    movies = get_movies_from_watchlist(friend_id)
    poster_paths = {m.id: get_poster_path(m.id) for m in movies}
    watch = {m.id for m in get_movies_from_watchlist(session["user_id"])}
    wish = {m.id for m in get_movies_from_wishlist(session["user_id"])}
    return render_template("friend-watchlist.html", friend=friend, watchlist=movies, watch=watch, wish=wish,
                           poster_paths=poster_paths)


@app.route('/friend_wishlist/<friend_id>')
@login_required
def friend_wishlist(friend_id):
    friend = get_person_by_id(friend_id)
    movies = get_movies_from_wishlist(friend_id)
    poster_paths = {m.id: get_poster_path(m.id) for m in movies}
    watch = {m.id for m in get_movies_from_watchlist(session["user_id"])}
    wish = {m.id for m in get_movies_from_wishlist(session["user_id"])}
    return render_template("friend-wishlist.html", friend=friend, wishlist=movies, watch=watch, wish=wish,
                           poster_paths=poster_paths)


@app.route('/friend_favourites/<friend_id>')
@login_required
def friend_favourites(friend_id):
    friend = get_person_by_id(friend_id)
    movies = get_movies_from_favourites(friend_id)
    poster_paths = {m.id: get_poster_path(m.id) for m in movies}
    watch = {m.id for m in get_movies_from_watchlist(session["user_id"])}
    wish = {m.id for m in get_movies_from_wishlist(session["user_id"])}
    return render_template("friend-favourites.html", friend=friend, favourites=movies, watch=watch, wish=wish,
                           poster_paths=poster_paths)


@app.route('/upload_photo', methods=["POST"])
@login_required
def upload_photo():
    user_id = session["user_id"]
    photo = get_photo(user_id)
    if photo is None:
        photo = metadata.Photos(person_id=user_id)
    photo.img_data = request.json
    insert(photo)
    return jsonify(success=True)


@app.route('/mark_as_useful/<review_id>', methods=["POST"])
@login_required
def mark_as_useful(review_id):
    if not has_marked_as_useful(session["user_id"], review_id):
        new_useful_item = metadata.Useful(person_id=session["user_id"], review_id=review_id)
        insert(new_useful_item)
        add_useful_badge(review_id)
    return jsonify(success=True)


if __name__ == "__main__":
    metadata.init_db('sqlite:///metadata.db')
    app.run('localhost', 8080, debug=True)
