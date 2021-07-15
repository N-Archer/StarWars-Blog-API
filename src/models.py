from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    favorites = db.relationship('Favorite', backref='user', lazy=True)


    def __repr__(self):
        return '<User %r,%r,%r,%r>' % (self.id, self.username, self.email,self.password)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "favorites": [favorite.serialize() for favorite in self.favorites]
            # do not serialize the password, its a security breach
        }

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(255), unique=False, nullable=False)
    entity_name = db.Column(db.String(255), unique=False, nullable=False)
    entity_id = db.Column(db.Integer, unique=False, nullable=False)
    # username = db.Column(db.String(120)), unique=True, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('user.username'))

    def __repr__(self):
        return '<Favorite %r,%r,%r,%r,%r>' % (self.id, self.entity_type, self.entity_name, self.entity_id,  self.username, self.username)

    def serialize(self):
        return {
            "id": self.id,
            # "username": self.username,
            "username": self.username,
            "entity_type": self.entity_type,
            "entity_name": self.entity_name,
            "entity_id":  self.entity_id,

            # do not serialize the password, its a security breach
        }