from sqlalchemy import MetaData, create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

metadata = MetaData()
engine = None
db_session = None
movie_engine = create_engine('sqlite:///movies.db', echo=True, connect_args={'check_same_thread': False})
Base = declarative_base(metadata=metadata)
MovieBase = declarative_base()
movie_db_session = sessionmaker(bind=movie_engine)()


def init_db(database):
    global engine, db_session
    engine = create_engine(database, echo=True, connect_args={'check_same_thread': False})
    db_session = sessionmaker(bind=engine)()


def create_all():
    Base.metadata.create_all(engine)


def get_session():
    return db_session


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    name = Column(String)
    surname = Column(String)
    password_hash = Column(String)


class Friends(Base):
    __tablename__ = 'friends'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer)
    friend_id = Column(Integer)


class Watchlist(Base):
    __tablename__ = 'watchlist'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer)
    movie_id = Column(Integer)
    rating = Column(Integer)


class Wishlist(Base):
    __tablename__ = 'wishlist'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer)
    movie_id = Column(Integer)


class Favourites(Base):
    __tablename__ = 'favourites'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer)
    movie_id = Column(Integer)


class Reviews(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer)
    movie_id = Column(Integer)
    text = Column(String)
    rating = Column(Integer)
    useful = Column(Integer, default=0)


class Useful(Base):
    __tablename__ = 'useful'
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer)
    person_id = Column(Integer)


class Photos(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer)
    img_data = Column(String)


class Movie(MovieBase):
    __tablename__ = 'movies'

    def __repr__(self) -> str:
        return "Movie: " + str(self.id) + self.title + str(self.year)

    def __eq__(self, other):
        return (
                self.__class__ == other.__class__ and
                self.id == other.id and
                self.title == other.title and
                self.year == other.year
        )

    id = Column(Integer, primary_key=True)
    title = Column(String)
    year = Column(Integer)


def get_movies_from_wishlist(person_id):
    wls = db_session.query(Wishlist).filter_by(person_id=person_id).all()
    movie_ids = [wl.movie_id for wl in wls]
    return movie_db_session.query(Movie).filter(Movie.id.in_(movie_ids)).order_by(Movie.title.asc()).all()


def get_movies_from_watchlist(person_id):
    wls = db_session.query(Watchlist).filter_by(person_id=person_id).all()
    movie_ids = [wl.movie_id for wl in wls]
    return movie_db_session.query(Movie).filter(Movie.id.in_(movie_ids)).order_by(Movie.title.asc()).all()


def get_movies_from_favourites(person_id):
    fvs = get_favourites(person_id)
    movie_ids = [fv.movie_id for fv in fvs]
    return movie_db_session.query(Movie).filter(Movie.id.in_(movie_ids)).order_by(Movie.title.asc()).all()


def get_favourites(person_id):
    return db_session.query(Favourites).filter_by(person_id=person_id).all()


def get_movies_by_title(title):
    return movie_db_session.query(Movie).filter(Movie.title.like(f'%{title}%')).order_by(Movie.year.desc()).all()


def get_user(username):
    return db_session.query(Users).filter_by(email=username).first()


def get_person_by_id(id):
    return db_session.query(Users).filter_by(id=id).first()


def get_friends(person_id):
    friends = db_session.query(Friends).filter_by(person_id=person_id).all()
    friend_ids = [f.friend_id for f in friends]
    return db_session.query(Users).filter(Users.id.in_(friend_ids)).all()


def get_feed(person_id):
    friends = db_session.query(Friends).filter_by(person_id=person_id).all()
    friend_ids = [f.friend_id for f in friends]
    reviews = db_session.query(Reviews).filter(Reviews.person_id.in_(friend_ids)).order_by(Reviews.id.desc()).all()
    posts = [{"id": r.id, "person_id": r.person_id, "movie_id": r.movie_id, "text": r.text, "rating": r.rating,
              "useful": r.useful} for r in reviews]
    for p in posts:
        person = db_session.query(Users).filter_by(id=p["person_id"]).first()
        p["name"] = person.name
        p["surname"] = person.surname
    for p in posts:
        movie = movie_db_session.query(Movie).filter_by(id=p["movie_id"]).first()
        p["title"] = movie.title
        p["year"] = movie.year
    return posts


def get_posts(person_id):
    reviews = db_session.query(Reviews).filter_by(person_id=person_id).order_by(Reviews.id.desc()).all()
    posts = [{"id": r.id, "person_id": r.person_id, "movie_id": r.movie_id, "text": r.text, "rating": r.rating,
              "useful": r.useful} for r in reviews]
    for p in posts:
        movie = movie_db_session.query(Movie).filter_by(id=p["movie_id"]).first()
        p["title"] = movie.title
        p["year"] = movie.year
    return posts


def insert(data):
    db_session.add(data)
    db_session.commit()


def delete(data):
    db_session.delete(data)
    db_session.commit()


def remove_watchlist_item(movie_id, person_id):
    removable = db_session.query(Watchlist).filter_by(movie_id=movie_id, person_id=person_id).first()
    delete(removable)


def remove_wishlist_item(movie_id, person_id):
    removable = db_session.query(Wishlist).filter_by(movie_id=movie_id, person_id=person_id).first()
    delete(removable)


def remove_favourites_item(movie_id, person_id):
    removable = db_session.query(Favourites).filter_by(movie_id=movie_id, person_id=person_id).first()
    delete(removable)


def make_watched(movie_id, person_id):
    wish_item = db_session.query(Wishlist).filter_by(movie_id=movie_id, person_id=person_id).first()
    watch_item = Watchlist(movie_id=movie_id, person_id=person_id)
    delete(wish_item)
    insert(watch_item)


def create_review(person_id, movie_id, text, rating):
    review = Reviews(person_id=person_id, movie_id=movie_id, text=text, rating=rating)
    insert(review)


def get_people(name, surname, person_id):
    return db_session.query(Users).filter_by(name=name, surname=surname).filter(Users.id != person_id).all()


def has_watchlist(movie_id, person_id):
    watch_item = db_session.query(Watchlist).filter_by(movie_id=movie_id, person_id=person_id).first()
    return watch_item is not None


def has_friendship(person_id, friend_id):
    friendship = db_session.query(Friends).filter_by(person_id=person_id, friend_id=friend_id).first()
    return friendship is not None


def has_review(movie_id, person_id):
    review = db_session.query(Reviews).filter_by(person_id=person_id, movie_id=movie_id).first()
    return review is not None


def has_wishlist(movie_id, person_id):
    wish_item = db_session.query(Wishlist).filter_by(movie_id=movie_id, person_id=person_id).first()
    return wish_item is not None


def has_favourites(movie_id, person_id):
    fave_item = db_session.query(Favourites).filter_by(movie_id=movie_id, person_id=person_id).first()
    return fave_item is not None


def get_stats(person_id):
    friends = db_session.query(Friends).filter_by(person_id=person_id).count()
    movies = db_session.query(Watchlist).filter_by(person_id=person_id).count()
    posts = db_session.query(Reviews).filter_by(person_id=person_id).count()
    useful = 0
    reviews = db_session.query(Reviews).filter_by(person_id=person_id).all()
    for r in reviews:
        useful += db_session.query(Useful).filter_by(review_id=r.id).count()
    stats = {"friends": friends, "movies": movies, "posts": posts, "useful": useful}
    return stats


def get_photo(person_id):
    return db_session.query(Photos).filter_by(person_id=person_id).first()


def has_marked_as_useful(person_id, review_id):
    useful_item = db_session.query(Useful).filter_by(person_id=person_id, review_id=review_id).first()
    return useful_item is not None


def add_useful_badge(review_id):
    db_session.query(Reviews).filter_by(id=review_id).update({Reviews.useful: Reviews.useful + 1})
    db_session.commit()


def get_friends_wishes(person_id):
    friends = get_friends(person_id)
    friends_wishes = {}
    for f in friends:
        wish_items = get_movies_from_wishlist(f.id)
        for w in wish_items:
            if w.id not in friends_wishes:
                friends_wishes[w.id] = []
            friends_wishes[w.id].append(f.name + " " + f.surname)
    return friends_wishes


def get_persons_useful(person_id):
    return db_session.query(Useful).filter_by(person_id=person_id).all()