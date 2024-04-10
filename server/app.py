#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class AllScientists(Resource):

    def get(self):
        scientists = Scientist.query.all()
        scientist_list = [scientist.to_dict(only=('id', 'name', 'field_of_study')) for scientist in scientists]
        return make_response(scientist_list, 200)
    
    def post(self):
        try:
            new_scientist = Scientist(name=request.json.get('name'), field_of_study=request.json.get('field_of_study'))
            db.session.add(new_scientist)
            db.session.commit()
            body = new_scientist.to_dict(rules=('-missions.scientist',))
            return make_response(body, 201)
        except:
            body = {"errors": ["validation errors"]}
            return make_response(body, 400)

api.add_resource(AllScientists, '/scientists')

class ScientistsByID(Resource):

    def get(self, id):
        scientist = db.session.get(Scientist, id)
        if scientist:
            body = scientist.to_dict(rules=('-missions.scientist', '-missions.planet.missions'))
            return make_response(body, 200)
        else:
            body = {"error": "Scientist not found"}
            return make_response(body, 404)
        
    def patch(self, id):
        scientist = db.session.get(Scientist, id)
        if scientist:
            try:
                for attr in request.json:
                    setattr(scientist, attr, request.json[attr])
                db.session.commit()
                body = scientist.to_dict(only=('id', 'name', 'field_of_study'))
                return make_response(body, 202)
            except:
                body = {"errors": ["validation errors"]}
                return make_response(body, 400)
        else:
            body = {"error": "Scientist not found"}
            return make_response(body, 404)
        
    def delete(self, id):
        scientist = db.session.get(Scientist, id)
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            body = {}
            return make_response(body, 204)
        else:
            body = {"error": "Scientist not found"}
            return make_response(body, 404)

api.add_resource(ScientistsByID, '/scientists/<int:id>')

class AllPlanets(Resource):

    def get(self):
        planets = Planet.query.all()
        planet_list = [planet.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star')) for planet in planets]
        return make_response(planet_list, 200)

api.add_resource(AllPlanets, '/planets')

class AllMissions(Resource):

    def post(self):
        try:
            new_mission = Mission(name=request.json.get('name'), scientist_id=request.json.get('scientist_id'), planet_id=request.json.get('planet_id'))
            db.session.add(new_mission)
            db.session.commit()
            body = new_mission.to_dict(rules=('-scientist.missions', '-planet.missions'))
            return make_response(body, 201)
        except:
            body = {"errors": ["validation errors"]}
            return make_response(body, 400)

api.add_resource(AllMissions, '/missions')


@app.route('/')
def home():
    return ''


if __name__ == '__main__':
    app.run(port=5555, debug=True)
