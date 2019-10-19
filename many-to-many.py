from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test3.db'
app.config['SECRET_KEY'] = "NoPasswordIsSafe"

db=SQLAlchemy(app)

movies_actors_association = db.Table('actors',
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True)
)

class Movie(db.Model):

    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(100), unique=True, nullable=False)
#    genre=db.Column(db.String(100), unique=True, nullable=False)
#    cast=db.Column(db.String(100), unique=True, nullable=False)

    #one-to-one relationship example
    genre_id=db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)
    genre=db.relationship('Genre', backref=db.backref('movie', lazy=True))

    #many-to-many relationship exmple
    cast=db.relationship('Actor', secondary=movies_actors_association, lazy=True, backref=db.backref('movies', lazy=True))

    def __repr__(self):
        return self.title

class Genre(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(20),unique=True,nullable=False)

    def __repr__(self):
        return self.name

class Actor(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100),unique=True,nullable=False)

    def __repr__(self):
        return '<Actor %r>' %self.name

db.create_all()

admin=Admin(app, name='movielog', template_mode='bootstrap3')
admin.add_view(ModelView(Movie, db.session))
admin.add_view(ModelView(Genre, db.session))
admin.add_view(ModelView(Actor, db.session))

if __name__=='__main__':
    app.run(debug=True)