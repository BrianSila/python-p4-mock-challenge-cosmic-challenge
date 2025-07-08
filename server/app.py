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


@app.route('/')
def home():
    return 'Welcome to the backend'

@app.route('/scientists', methods=['Get'])
def get_scientists():

    scientists = Scientist.query.all()

    if not scientists:
        return jsonify({"error": "Scientists not found"}), 404
    
    scientist_list = [
        {
            'id': scientist.id,
            'name': scientist.name,
            'field_of_study': scientist.field_of_study
        } for scientist in scientists
    ]

    return jsonify(scientist_list), 200

@app.route('/scientists/<int:id>', methods=['GET'])
def get_scientist(id):

    scientist = db.session.get(Scientist, id)

    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    scientist_data = {
        'id': scientist.id,
        'name': scientist.name,
        'field_of_study': scientist.field_of_study,
        'missions': [
            {
                'id': mission.id,
                'name': mission.name,
                'planet': {
                    'distance_from_earth': mission.planet.distance_from_earth,
                    'id': mission.planet.id,
                    'name': mission.planet.name,
                    'nearest_star': mission.planet.nearest_star
                } if mission.planet else None,
                'planet_id': mission.planet_id,
                'scientist_id': mission.scientist_id
            } for mission in scientist.missions
        ]
    }

    return jsonify(scientist_data), 200

@app.route('/scientists', methods=['POST'])
def create_scientist():

    data = request.get_json()

    if not data or not data.get('name') or not data.get('field_of_study'):
        return jsonify({"errors": ["validation errors"]}), 400
    
    try:
        new_scientist = Scientist(
            name=data.get('name'),
            field_of_study=data.get('field_of_study')
        )

        db.session.add(new_scientist)
        db.session.commit()
    except ValueError:
        return jsonify({"errors": ["validation errors"]}), 400
    
    return jsonify({
            'id': new_scientist.id,
            'name': new_scientist.name,
            'field_of_study': new_scientist.field_of_study
    }), 201

@app.route('/scientists/<int:id>', methods=['PATCH'])
def update_scientist(id):

    record = Scientist.query.filter(Scientist.id == id).first()

    if not record:
        return jsonify({"error": "Scientist not found"}), 404
    
    data = request.get_json()

    if not data or not data.get('name') or not data.get('field_of_study'):
        return jsonify({"errors": ["validation errors"]}), 400
    
    try: 
        for attr, value in data.items():
            setattr(record, attr, value)
        db.session.add(record)
        db.session.commit()
    except ValueError:
        return jsonify({"errors": ["validation errors"]}), 400
    
    return jsonify({
            'id': record.id,
            'name': record.name,
            'field_of_study': record.field_of_study,
            'missions': []
    }), 202

@app.route('/scientists/<int:id>', methods=['DELETE'])
def delete_Scientist(id):

    scientist = db.session.get(Scientist, id)

    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404
    
    db.session.delete(scientist)
    db.session.commit()

    return jsonify({}), 204
    
@app.route('/planets', methods=['GET'])
def get_planets():

    planets = Planet.query.all()

    if not planets:
        return jsonify({"errors": "Planets not found"}), 404
    
    planets_list = [
        {
            'id': planet.id,
            'name': planet.name,
            'distance_from_earth': planet.distance_from_earth,
            'nearest_star': planet.nearest_star
        } for planet in planets
    ]

    return jsonify(planets_list), 200

@app.route('/missions', methods=['POST'])
def create_mission():

    data = request.get_json()

    if not data or not data.get('name') or not data.get('scientist_id') or not data.get('planet_id'):
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        new_mission =  Mission(
            name=data.get('name'),
            scientist_id=data.get('scientist_id'),
            planet_id=data.get('planet_id')
        )

        db.session.add(new_mission)
        db.session.commit()
    except ValueError:
        return jsonify({"errors": ["validation errors"]}), 404
    
    planet = db.session.get(Planet, new_mission.planet_id)
    scientist = db.session.get(Scientist, new_mission.scientist_id)
    return jsonify({
        'id': new_mission.id,
        'name': new_mission.name,
        'scientist_id': new_mission.scientist_id,
        'planet_id': new_mission.planet_id,
        'planet': {
            'id': planet.id,
            'name': planet.name,
            'distance_from_earth': planet.distance_from_earth,
            'nearest_star': planet.nearest_star
        } if planet else None,
        'scientist': {
            'id': scientist.id,
            'name': scientist.name,
            'field_of_study': scientist.field_of_study
        } if scientist else None
    }), 201

if __name__ == '__main__':
    app.run(port=5555, debug=True)
