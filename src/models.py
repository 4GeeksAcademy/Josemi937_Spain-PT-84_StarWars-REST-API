from flask_sqlalchemy import SQLAlchemy 


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    planet_favorite = db.relationship('FavoritePlanets', back_populates='users', cascade="all, delete-orphan")
    people_favorite = db.relationship('FavoritePeople', back_populates='users', cascade="all, delete-orphan")

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class People(db.Model) :
    __tablename__ = 'people'
    id = db.Column (db.Integer, primary_key=True)      
    name = db.Column(db.String(50), unique=True, nullable=False)
    age = db.Column(db.Integer, unique=False, nullable=False)
    favorite_people = db.relationship('FavoritePeople', back_populates='people_favorites')

    def __repr__(self):
        return f'El personaje {self.id} con nombre {self.name}'
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            
        }
class Planets(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    population = db.Column(db.String(100), unique=False, nullable=False)
    favorite_planets = db.relationship('FavoritePlanets', back_populates='planets_favorites')

    def __repr__(self):
        return f'El planeta {self.id} con nombre {self.name}'
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population
            
        }
class FavoritePlanets(db.Model):
        __tablename__='favorite_planets'
        id= db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        users = db.relationship('User', back_populates='planet_favorite')
        planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
        planets_favorites = db.relationship('Planets', back_populates='favorite_planets')

        def __repr__(self):
            return f'Al usuario {self.user_id} le gusta el planeta {self.planet_id}'
        def serialize(self):
            return {
                'id': self.id,
                'user_id' : self.user_id,
                'planet_id' : self.planet_id
            }
class FavoritePeople(db.Model):
        __tablename__='favorite_people'
        id= db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        users = db.relationship('User', back_populates='people_favorite')
        people_id = db.Column(db.Integer, db.ForeignKey('people.id'))
        people_favorites = db.relationship('People', back_populates='favorite_people')

        def __repr__(self):
            return f'Al usuario {self.user_id} le gusta el personaje {self.people_id}'
        def serialize(self):
            return {
                'id': self.id,
                'user_id' : self.user_id,
                'people_id' : self.people_id
            }   