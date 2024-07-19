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
from models import db, User, Characters, Vehicles, Planets, Favourites
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

# ----------ALL GUET-----------------

@app.route('/user', methods=['GET'])
def get_all_users():
    users = User.query.all()
    users_serialized = [user.serialize() for user in users]
    return jsonify(users_serialized), 200

@app.route('/user/<int:id>', methods=['GET'])
def get_one_user(id):
    user = User.query.get(id)
    return jsonify({'user': user.serialize()}), 200

@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Characters.query.all()
    characters_serialized = [character.serialize() for character in characters]
    return jsonify(characters_serialized), 200

@app.route('/characters/<int:id>', methods=['GET'])
def get_one_character(id):
    character = Characters.query.get(id)
    return jsonify({"character": character.serialize()}), 200

@app.route('/vehicles', methods=['GET'])
def get_all_vehicles():
    vehicles = Vehicles.query.all()
    vehicles_serialized = [vehicle.serialize() for vehicle in vehicles]
    return jsonify(vehicles_serialized), 200

@app.route('/vehicles/<int:id>', methods=['GET'])
def get_one_vehicle(id):
    vehicle = Vehicles.query.get(id)
    return jsonify({"vehicle": vehicle.serialize()})

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    planets_serialized = [planet.serialize() for planet in planets]
    return jsonify(planets_serialized), 200

@app.route('/planets/<int:id>', methods=['GET'])
def get_one_planet(id):
    planet = Planets.query.get(id)
    return jsonify({"planet": planet.serialize()})

@app.route('/favourites', methods=['GET'])
def get_all_favourites():
    favourites = Favourites.query.all()
    favourites_serialized = [favourite.serialize() for favourite in favourites]
    return jsonify(favourites_serialized), 200

# -----------ALL POST---------------

@app.route('/planetfavorite/<int:user_id>/<int:planet_id>', methods=['POST'])
def get_favorite_planet(user_id, planet_id):

    body = request.json

    user_id = body.get("user_id", None)
    planet_id = body.get("planet_id", None)

    if user_id is None or planet_id is None:
        return jsonify({"error", "Missing values"}), 400
    
    planet_favorite_user_exist = PlanetFavorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if planet_favorite_user_exist is not None:
        return jsonify({"error": f"planet {planet_id} and user {user_id} already exists"}),400

    planet_favorites = PlanetFavorite(user_id=user_id, planet_id=planet_id)

    try:
        db.session.add(planet_favorites)
        db.session.commit()
        db.session.refresh(planet_favorites)

        return jsonify({"message": f"planet_favorite {planet_id} with user {user_id} created successfully!"}), 201
    except Exception as error:
        return jsonify({"error": f"{error}"}),500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
