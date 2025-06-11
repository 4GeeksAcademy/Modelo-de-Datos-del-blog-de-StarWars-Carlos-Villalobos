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
from models import db, User, Characters, Planets, Favorites
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

#-------------------------ENDPOINT PARA RECUPERAR TODOS LOS USUARIOS--------------------------------------

@app.route('/user', methods=['GET'])
def get_user():

    user_all = User.query.all()
    results = list(map(lambda item: item.serialize(), user_all))
    # print(user_all)

    response_body = {
        "msg": "ok",
        "results": results
    }

    return jsonify(response_body), 200

#-------------------------ENDPOINT PARA RECUPERAR TODOS LOS PERSONAJES--------------------------------------

@app.route('/people', methods=['GET'])
def get_people():

    people_all = Characters.query.all()
    results = list(map(lambda item: item.serialize(), people_all))
    # print(user_all)

    response_body = {
        "msg": "ok",
        "results": results
    }

    return jsonify(response_body), 200

#--------------------------ENDPOINT PARA RECUPERAR SOLO 1 PERSONAJE------------------------------------------

@app.route('/people/<int:id>', methods=['GET'])
def get_one_people(id):
    
    people_item = Characters.query.get(id)
    if not people_item:
        return jsonify('Character not found'), 400

    return jsonify(people_item.serialize()), 200

#-------------------------ENDPOINT PARA RECUPERAR TODOS LOS PLANETAS--------------------------------------
@app.route('/planets', methods=['GET'])
def get_planets():

    planets_all = Planets.query.all()
    results = list(map(lambda item: item.serialize(), planets_all))
    # print(user_all)

    response_body = {
        "msg": "ok",
        "results": results
    }

    return jsonify(response_body), 200

#--------------------------ENDPOINT PARA RECUPERAR SOLO 1 PLANETA------------------------------------------

@app.route('/planets/<int:id>', methods=['GET'])
def get_one_planet(id):
    
    planet_item = Planets.query.get(id)
    if not planet_item:
        return jsonify('Planet not found'), 400

    return jsonify(planet_item.serialize()), 200

#--------------------------ENDPOINT PARA AÑADIR FAVORITOS------------------------------------------

@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.get_json() 

    # Validación
    if not data or 'user_id' not in data:
        raise APIException("Missing user_id in request body", status_code=400)

    user_id = data['user_id']
    character_id = data.get('character_id') 
    planets_id = data.get('planets_id')

    if not character_id and not planets_id:
        raise APIException("Either character_id or planets_id must be provided", status_code=400)
    if character_id and planets_id:
        raise APIException("Cannot favorite both a character and a planet at once", status_code=400)


    user = db.session.get(User, user_id)
    if not user:
        raise APIException(f"User with id {user_id} not found", status_code=404)

    new_favorite = None

    if character_id:

        character = db.session.get(Characters, character_id)
        if not character:
            raise APIException(f"Character with id {character_id} not found", status_code=404)
        
        
        new_favorite = Favorites(user_id=user_id, character_id=character_id, planets_id=None) 

    elif planets_id:
       
        planet = db.session.get(Planets, planets_id)
        if not planet:
            raise APIException(f"Planet with id {planets_id} not found", status_code=404)
        
        
        new_favorite = Favorites(user_id=user_id, character_id=None, planets_id=planets_id) 

    
    try:
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify(new_favorite.serialize()), 201 # 201 Created
    except Exception as e:
        db.session.rollback() 
        e
        if "UniqueConstraint" in str(e): # 
            raise APIException("This item is already in favorites for this user", status_code=409) 
        else:
        
            raise APIException(f"An error occurred: {str(e)}", status_code=500)



#--------------------------ENDPOINT PARA OBTENER FAVORITOS------------------------------------------
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise APIException(f"User with id {user_id} not found", status_code=404)
    
    favorites = user.favorites 
    
    serialized_favorites = [fav.serialize() for fav in favorites]

    return jsonify(serialized_favorites), 200

#--------------------------ENDPOINT PARA ELIMINAR FAVORITOS------------------------------------------
@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    favorite_to_delete = db.session.get(Favorites, favorite_id)

    if not favorite_to_delete:
        raise APIException(f"Favorite with id {favorite_id} not found", status_code=404)

    try:
        db.session.delete(favorite_to_delete)
        db.session.commit()
        return jsonify({"msg": "Favorite deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        raise APIException(f"An error occurred while deleting favorite: {str(e)}", status_code=500)


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
