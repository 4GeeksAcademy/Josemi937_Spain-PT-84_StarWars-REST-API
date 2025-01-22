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
from models import db, User, People, Planets, FavoritePlanets, FavoritePeople
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



@app.route('/user')
def get_user():
    all_user = User.query.all()
    all_user_serialize = []
    for user in all_user:
        all_user_serialize.append(user.serialize())
    print (all_user_serialize)
    return jsonify ({'msg':  'get user ok', 'data': all_user_serialize})


@app.route('/people')
def get_people():
    all_people = People.query.all()
    all_people_serialize = []
    for person in all_people:
        all_people_serialize.append(person.serialize())
    print (all_people_serialize)
    return jsonify ({'msg':  'get people ok', 'data': all_people_serialize})

@app.route('/people/<int:people_id>')
def get_single_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({'msg' : f'El personaje con id {people_id} no existe'}), 400
    return jsonify({'data': person.serialize()})

@app.route('/people', methods=['POST'])
def add_person():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify ({'msg' : 'Debes enviar name y age en el body'}), 400
    if 'name' not in body:
        return jsonify ({'msg': 'El campo name es obligatorio'}), 400
    if 'age' not in body:
        return jsonify ({'msg': 'El campo age es obligatorio'}), 400
    new_person = People()
    new_person.name = body['name']
    new_person.age = body ['age']
    db.session.add(new_person)
    db.session.commit()
    print (new_person)
    print(type(new_person))
    return jsonify ({'msg': 'new person added', 'data' : new_person.serialize()})


@app.route('/planets')
def get_planets():
    all_planets = Planets.query.all()
    all_planets_serialize = []
    for planets in all_planets:
        all_planets_serialize.append(planets.serialize())
    print (all_planets_serialize)
    return jsonify ({'msg':  'get planets ok', 'data': all_planets_serialize})

@app.route('/planets/<int:planets_id>')
def get_single_planet(planets_id):
    planet = Planets.query.get(planets_id)
    if planet is None:
        return jsonify({'msg' : f'El planeta con id {planets_id} no existe'}), 400
    return jsonify({'data': planet.serialize()})

@app.route('/planets', methods=['POST'])
def add_planet():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify ({'msg' : 'Debes enviar name y population en el body'}), 400
    if 'name' not in body:
        return jsonify ({'msg': 'El campo name es obligatorio'}), 400
    if 'population' not in body:
        return jsonify ({'msg': 'El campo population es obligatorio'}), 400
    new_planet = Planets()
    new_planet.name = body['name']
    new_planet.population = body ['population']
    db.session.add(new_planet)
    db.session.commit()
    print (new_planet)
    print(type(new_planet))
    return jsonify ({'msg': 'new planet added', 'data' : new_planet.serialize()})
    

@app.route('/user/<int:user_id>/favorites')
def get_favorites_by_user(user_id):
    
    favorite_planets = FavoritePlanets.query.filter_by(user_id=user_id).all()
    favorite_planets_serialize = []
    for favorite in favorite_planets:
        favorite_planets_serialize.append(favorite.planets_favorites.serialize())
    favorite_people = FavoritePeople.query.filter_by(user_id=user_id).all()
    favorite_people_serialize = []
    for favorite in favorite_people:
        favorite_people_serialize.append(favorite.people_favorites.serialize())
    return jsonify({
        'favorite_planets': favorite_planets_serialize,
        'favorite_people': favorite_people_serialize,
        'user': favorite_planets[0].users.serialize() if favorite_planets else None
    })


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get('user_id')  
    if not user_id:
        return jsonify({"msg": "user_id es necesario"}), 400
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": f"El planeta con ID {planet_id} no existe"}), 404
    existing_favorite = FavoritePlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if existing_favorite:
        return jsonify({"msg": "Este planeta ya está en tus favoritos"}), 400
    new_favorite = FavoritePlanets(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({
        "msg": "Planeta favorito añadido con éxito",
        "data": new_favorite.serialize()  
    }), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    body = request.get_json(silent=True)
    if not body or 'user_id' not in body:
        return jsonify({'msg': 'user_id es necesario'}), 400
    user_id = body['user_id']
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': f'El usuario con ID {user_id} no existe'}), 404
    people = People.query.get(people_id)
    if people is None:
        return jsonify({'msg': f'El personaje con ID {people_id} no existe'}), 404
    existing_favorite = FavoritePeople.query.filter_by(user_id=user_id, people_id=people_id).first()
    if existing_favorite:
        return jsonify({'msg': f'El personaje {people.name} ya está en los favoritos del usuario {user_id}'}), 400
    new_favorite = FavoritePeople(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({'msg': 'Personaje favorito añadido con éxito', 'data': new_favorite.serialize()}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    body = request.get_json(silent=True)
    if not body or 'user_id' not in body:
        return jsonify({'msg': 'user_id es necesario'}), 400
    user_id = body['user_id']
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': f'El usuario con ID {user_id} no existe'}), 404
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({'msg': f'El planeta con ID {planet_id} no existe'}), 404
    favorite_planet = FavoritePlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite_planet is None:
        return jsonify({'msg': f'El planeta con ID {planet_id} no está en los favoritos del usuario {user_id}'}), 404
    db.session.delete(favorite_planet)
    db.session.commit()
    return jsonify({'msg': f'El planeta con ID {planet_id} ha sido eliminado de los favoritos del usuario {user_id}'}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    body = request.get_json(silent=True)
    if not body or 'user_id' not in body:
        return jsonify({'msg': 'user_id es necesario'}), 400
    user_id = body['user_id']
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'msg': f'El usuario con ID {user_id} no existe'}), 404
    person = People.query.get(people_id)
    if person is None:
        return jsonify({'msg': f'El personaje con ID {people_id} no existe'}), 404
    favorite_person = FavoritePeople.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite_person is None:
        return jsonify({'msg': f'El personaje con ID {people_id} no está en los favoritos del usuario {user_id}'}), 404
    db.session.delete(favorite_person)
    db.session.commit()
    return jsonify({'msg': f'El personaje con ID {people_id} ha sido eliminado de los favoritos del usuario {user_id}'}), 200

@app.route('/planets', methods=['POST'])
def add_new_planet():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar el campo name y population en el body'}), 400
    if 'name' not in body or 'population' not in body:
        return jsonify({'msg': 'Los campos name y population son obligatorios'}), 400
    new_planet = Planets(
        name=body['name'],
        population=body['population']
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({'msg': 'Nuevo planeta agregado', 'data': new_planet.serialize()}), 201



@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    body = request.get_json(silent=True)
    if not body:
        return jsonify({'msg': 'Debes enviar los datos a modificar'}), 400
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({'msg': f'El planeta con ID {planet_id} no existe'}), 404
    if 'name' in body:
        planet.name = body['name']
    if 'population' in body:
        planet.population = body['population']
    db.session.commit()
    return jsonify({'msg': 'Planeta actualizado', 'data': planet.serialize()}), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({'msg': f'El planeta con ID {planet_id} no existe'}), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({'msg': f'El planeta con ID {planet_id} ha sido eliminado'}), 200

@app.route('/people', methods=['POST'])
def add__new_person():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({'msg': 'Debes enviar los campos name y age en el body'}), 400
    if 'name' not in body or 'age' not in body:
        return jsonify({'msg': 'Los campos name y age son obligatorios'}), 400
    new_person = People(
        name=body['name'],
        age=body['age']
    )
    db.session.add(new_person)
    db.session.commit()
    return jsonify({'msg': 'Nuevo personaje agregado', 'data': new_person.serialize()}), 201

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    body = request.get_json(silent=True)
    if not body:
        return jsonify({'msg': 'Debes enviar los datos a modificar'}), 400
    person = People.query.get(people_id)
    if person is None:
        return jsonify({'msg': f'El personaje con ID {people_id} no existe'}), 404
    if 'name' in body:
        person.name = body['name']
    if 'age' in body:
        person.age = body['age']
    db.session.commit()
    return jsonify({'msg': 'Personaje actualizado', 'data': person.serialize()}), 200

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({'msg': f'El personaje con ID {people_id} no existe'}), 404
    db.session.delete(person)
    db.session.commit()
    return jsonify({'msg': f'El personaje con ID {people_id} ha sido eliminado'}), 200






# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
