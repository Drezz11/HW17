# app.py
import json

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False}
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre = fields.Nested(GenreSchema)
    director = fields.Nested(DirectorSchema)



api = Api(app)

movie_ns = api.namespace('movies')
genre_ns = api.namespace('genres')
director_ns = api.namespace('directors')


@movie_ns.route('/')
class MovieView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        query = Movie.query
        if director_id:
            query = query.filter(Movie.director_id == director_id)
        if genre_id:
            query = query.filter(Movie.genre_id == genre_id)

        return MovieSchema(many=True).dump(query.all()), 200

    def post(self):
        data = request.json
        try:
            db.session.add(Movie(**data))
            db.session.commit()
            return "Успешно", 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return "Неуспешно", 500

@movie_ns.route('/<int:id>')
class MovieView(Resource):
    def get(self, id):
        result = Movie.query(Movie).filter(Movie.id == id).all()
        if len(result):
            return MovieSchema().dump(result), 200
        else:
            return json.dumps({}), 200

    def put(self, id):
        data = request.json
        try:
            result = Movie.query.filter(Movie.id == id).one()
            result.title = data.get('title')
            db.session.add(result)
            db.session.commit()
            return "Обновилось", 200
        except Exception:
            db.session.rollback()
            return "Не  обновилось", 500

    def delete(self, id):
        try:
            result = Movie.query.filter(Movie.id == id).one()
            db.session.delete(result)
            db.session.commit()
            return "Удалилось", 200
        except Exception:
            db.session.rollback()
            return "Не удалилось", 500

@director_ns.route("/")
class DirectorView(Resource):
    def get(self):
        return DirectorSchema(many=True).dumps(Director.query.all())

    def post(self):
        data = request.json
        try:
            db.session.add(Director(**data))
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()

@director_ns.route("/<int:id>")
class DirectorView(Resource):
    def get(self, id):
        result = Director.query(Director).filter(Director.id == id).all()
        if len(result):
            return DirectorSchema().dump(result), 200
        else:
            return json.dumps({}), 200
@genre_ns.route("/")
class GenreView(Resource):
    def get(self):
        return GenreSchema(many=True).dumps(Genre.query.all())

    def post(self):
        data = request.json
        try:
            db.session.add(Genre(**data))
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()

@genre_ns.route("/<int:id>")
class GenreView(Resource):
    def get(self, id):
        result = Genre.query(Genre).filter(Genre.id == id).all()
        if len(result):
            return GenreSchema().dump(result), 200
        else:
            return json.dumps({}), 200




if __name__ == '__main__':
    app.run(debug=True)
