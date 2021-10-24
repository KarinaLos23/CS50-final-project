import flask
import pytest
from flask import request
from werkzeug.security import generate_password_hash

import main
from metadata import *


@pytest.fixture(autouse=True)
def do_something(request):
    init_db('sqlite:///:memory:')
    create_all()


def test_login_get():
    main.app.config['TESTING'] = True
    client = main.app.test_client()
    rv = client.get('/')
    # print(rv.data)
    assert b'Enter email' in rv.data


def test_login_successfully():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        password = "test_password"
        user = Users(id=152, email="test_user", name="aaaa", surname="bbbbb", password_hash=generate_password_hash(password))
        get_session().add(user)
        rv = login(client, "test_user", password)
        print(rv.data)
        assert flask.session['user_id'] == 152
        assert request.path == '/home'


def test_register_successfully():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        rv = register(client, "aaaa", "bbbbb", "test_user", "test_password", "test_password")
        print(rv.data)
        user = get_session().query(Users).filter_by(email="test_user").first()
        assert user.name == "aaaa" and user.surname == "bbbbb" and user.email == "test_user"
        assert request.path == '/'


def login(client, username, password):
    return client.post('/', data=dict(
        email=username,
        pwd=password
    ), follow_redirects=True)


def register(client, name, surname, email, pwd, pwdconf):
    return client.post('/register', data=dict(
        name=name,
        surname=surname,
        email=email,
        pwd=pwd,
        pwdconf=pwdconf
    ), follow_redirects=True)


def test_post_to_wishlist():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        rv = post_to_wishlist(client, "Dama de noche")
        print(rv.data)
        expected = [Movie(id=15724, title="Dama de noche", year=1993)]
        assert get_movies_from_wishlist(person_id=0) == expected


def post_to_wishlist(client, title):
    return client.post('/wishlist/0', data=dict(
        title=title
    ), follow_redirects=True)


def test_post_to_watchlist():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        rv = post_to_watchlist(client, "Dama de noche")
        print(rv.data)
        expected = [Movie(id=15724, title="Dama de noche", year=1993)]
        assert get_movies_from_watchlist(person_id=0) == expected


def post_to_watchlist(client, title):
    return client.post('/watchlist/0', data=dict(
        title=title
    ), follow_redirects=True)


def test_post_to_favourites():
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        rv = post_to_favourites(client, "Dama de noche")
        print(rv.data)
        expected = [Movie(id=15724, title="Dama de noche", year=1993)]
        assert get_movies_from_favourites(person_id=0) == expected


def post_to_favourites(client, title):
    return client.post('/favourites/0', data=dict(
        title=title
    ), follow_redirects=True)