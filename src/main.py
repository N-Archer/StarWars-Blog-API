"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import datetime
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorite
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route("/login", methods=["POST"])
def log_in():
    # username = request.json.get("username", None)
    credentials = request.get_json()
    username = credentials.get ("username", None)
    # password = request.json.get("password", None)
    password = credentials.get ("password", None)
    # Query your database for username and password
    user = User.query.filter_by(username=username, password=password).first()
    if user is None:
        # the user was not found on the database
        return jsonify({"msg": "Bad username or password"}), 401
    
    # create a new token with the user id inside
    expires = datetime.timedelta(days=7)
    access_token = create_access_token(identity=user.username, expires_delta=expires)
    return jsonify({ "token": access_token, "user_id": user.username })

@app.route('/auth', methods=['GET'])
@jwt_required()
def run_auth():
    current_user_id = get_jwt_identity()

    return jsonify(user=current_user_id), 200

@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    response_body = {
        "users": all_users
    }

    return jsonify(response_body), 200

@app.route('/<user>/favorites', methods=['GET'])
def get_favorites(user):
    if user == None:
        raise APIException("User Not Found", status_code=404)
    favorites = Favorite.query.filter_by(username=user)
    all_favorites = list(map(lambda x: x.serialize(), favorites))
    response_body = {
        "favorites": all_favorites
    }

    return jsonify(response_body), 200

@app.route('/favorite/planet/<int:id>', methods=["POST", "DELETE"])
def change_planet(id):
    request_body = request.get_json()
    if request_body is None or request_body == {}:
        raise APIException("Empty Body", status_code=404)
    if request.method == "POST":
        new_planet = Favorite(entity_name=request_body['entity_name'], entity_type="planet", entity_id=id, username=request_body['username'])
        db.session.add(new_planet)
        db.session.commit()
    if request.method == 'DELETE':
        deleted_planet = Favorite.query.filter_by(username=request_body["username"], entity_type="planet", entity_id=id).first()
        if deleted_planet is None:
            raise APIException("User Not Found", status_code=404)
        db.session.delete(deleted_planet)
        db.session.commit()
    favorites = Favorite.query.filter_by(username=request_body['username'])
    all_favorites = list(map(lambda x: x.serialize(), favorites))
    response_body = {
        "Favorites": all_favorites
    }

    return jsonify(response_body), 200  

@app.route('/favorite/person/<int:id>', methods=["POST", "DELETE"])
def change_person(id):
    request_body = request.get_json()

    if request_body is None or request_body == {}:
        raise APIException("Empty Body", status_code=404)
    if request.method == "POST":
        record = Favorite.query.filter_by(username=request_body['username'], entity_name=request_body['entity_name']).first()
        if record:
            raise APIException("Duplicate Entity_Name", status_code=409)
        new_person = Favorite(entity_name=request_body['entity_name'], entity_type="person", entity_id=id, username=request_body['username'])
        db.session.add(new_person)
        db.session.commit()
    if request.method == 'DELETE':
        deleted_person = Favorite.query.filter_by(username=request_body["username"], entity_type="person", entity_id=id).first()
        if deleted_person is None:
            raise APIException("User Not Found", status_code=404)
        db.session.delete(deleted_person)
        db.session.commit() 
    favorites = Favorite.query.filter_by(username=request_body['username'])
    all_favorites = list(map(lambda x: x.serialize(), favorites))
    response_body = {
        "Favorites": all_favorites
    }

    return jsonify(response_body), 200  



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
