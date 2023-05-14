"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Person, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def get_all_people():
    people = Person.query.all()
    return jsonify([person.serialize() for person in people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Person.query.get(people_id)
    if person is None:
        raise APIException('Person not found', status_code=404)
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException('Planet not found', status_code=404)
    return jsonify(planet.serialize()), 200

# since there's no authentication, this is a workaround assuming user id 1 is making the requests
# users created in order to test POST requests
current_user_id = 2


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    favorites = Favorite.query.filter_by(user_id=current_user_id).all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException('Planet not found', status_code=404)

    new_favorite = Favorite(user_id=current_user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    person = Person.query.get(people_id)
    if planet is None:
        raise APIException('Person not found', status_code=404)

    new_favorite = Favorite(user_id=current_user_id, person_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    favorite = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if favorite is None:
        raise APIException('Favorite not found', status_code=404)

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"success": True}), 204

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    favorite = Favorite.query.filter_by(user_id=current_user_id, person_id=people_id).first()
    if favorite is None:
        raise APIException('Favorite not found', status_code=404)

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"success": True}), 204

# creating post endpoints for planets and people - testing Postman purposes
@app.route('/people', methods=['POST'])
def create_person():
    data = request.get_json()
    if not data:
        raise APIException( 'Invalid or missing JSON data', status_code=400)

    new_person = Person(name=data.get('name'), age=data.get('age'), gender=data.get('gender'))

    db.session.add(new_person)
    db.session.commit()

    return jsonify(new_person.serialize()), 201

@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    if not data:
        raise APIException( 'Invalid or missing JSON data', status_code=400)

    new_planet = Planet(name=data.get('name'), dimension=data.get('dimension'), terrain=data.get('terrain'))

    db.session.add(new_planet)
    db.session.commit()

    return jsonify(new_planet.serialize()), 201

@app.route('/users/register', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        email=data.get('email'),
        password=data.get('password'),
        name=data.get('name')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
