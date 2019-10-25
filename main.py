from flask import Flask, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_restful import Resource, Api, reqparse
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import ModelSchema

app = Flask(__name__)
api = Api(app)
ma = Marshmallow(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie.db'
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SECRET_KEY'] = "NoPasswordIsSafe"

db = SQLAlchemy(app)

movies_actors_association = db.Table('actors',
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True)
)


class Movie(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)
    genre = db.relationship('Genre', backref=db.backref('movie', lazy=True))
    cast = db.relationship('Actor', secondary=movies_actors_association, lazy=True,
                         backref=db.backref('movies', lazy=True))

    def __repr__(self):
        return self.title


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),unique=True,nullable=False)

    def __repr__(self):
        return self.name


class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True,nullable=False)

    def __repr__(self):
        return self.name


#flask marshmallow serializer
class MovieSchema(ModelSchema):
    class Meta:
        model = Movie


db.create_all()


movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()


#Flask Admin
admin = Admin(app, name='movielog', template_mode='bootstrap3')
admin.add_view(ModelView(Movie, db.session))
admin.add_view(ModelView(Genre, db.session))
admin.add_view(ModelView(Actor, db.session))


#Flask Restful
class OneMovie(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('movie_id', type=int, required=True)
        self.args = parser.parse_args()

        movie = Movie.query.filter(Movie.id == self.args['movie_id']).first()
        if not movie:
            return abort(404, 'Movie with id: {} does not exist in database.'.format(self.args['movie_id']))

        return jsonify(movies=movie_schema.dump(movie))

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True),
        parser.add_argument('genre_id', type=int, required=True),
        parser.add_argument('cast_id', action='append', type=str)
        self.args = parser.parse_args()

        title = self.args['title']
        genre_id = self.args['genre_id']

        existing_movie = Movie.query.filter(Movie.title == title).first()
        if existing_movie:
            return abort(400, 'Movie with title: {} already exists in database.'.format(self.args['title']))

        movie = Movie(
            title=title,
            genre_id=genre_id
        )

        if self.args['cast_id']:
            for id in self.args['cast_id']:
                actor = Actor.query.filter(Actor.id == id).first()
                if not actor:
                    return abort(404, 'Actor with id: {} does not exist in database.'.format(id))
                movie.cast.append(actor)
                db.session.commit()

        try:
            db.session.add(movie)
            db.session.commit()
        except:
            return abort(500, 'An error occurred while trying to add new movie to database.')

        return jsonify(message='New movie has been created.')


class MovieList(Resource):

    def get(self):
        movies = Movie.query.all()

        return jsonify(movie=movies_schema.dump(movies))


api.add_resource(OneMovie, '/movie')
api.add_resource(MovieList, '/movie/all')

if __name__=='__main__':
    app.run(debug=True, port = 5010)