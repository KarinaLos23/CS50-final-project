import pytest
from metadata import *


@pytest.fixture(autouse=True)
def do_something(request):
    init_db('sqlite:///:memory:')
    create_all()


def test_get_wishlist():
    assert get_movies_from_wishlist(person_id=123) == []
    wl = Wishlist(id=0, person_id=100, movie_id=15724)
    get_session().add(wl)
    expected = Movie(id=15724, title="Dama de noche", year=1993)
    assert get_movies_from_wishlist(person_id=100) == [expected]


def test_get_watchlist():
    assert get_movies_from_watchlist(person_id=123) == []
    wl = Watchlist(id=0, person_id=100, movie_id=15724)
    get_session().add(wl)
    expected = Movie(id=15724, title="Dama de noche", year=1993)
    assert get_movies_from_watchlist(person_id=100) == [expected]