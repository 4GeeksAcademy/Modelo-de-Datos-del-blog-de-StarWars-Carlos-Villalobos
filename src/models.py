from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  String, Boolean, ForeignKey, Text, Date, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime


db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    favorites = relationship('Favorites', back_populates='user', lazy='select') #Relación de favorito
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "favorites": self.favorites,
            "created_at": self.created_at
            # do not serialize the password, its a security breach
        }

class Characters(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False) # URL de la imagen/video
    description: Mapped[str] = mapped_column(Text, nullable=True) # Descripción del personaje
    birthdate: Mapped[date] = mapped_column(Date, nullable=False)

    # Clave foránea: Un Character puede ser un favorito
    favorites = relationship('Favorites', back_populates='characters') 
    

    def serialize(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "description": self.description,
            "birthdate": self.birthdate,
        }
    
class Planets(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False) # URL de la imagen/video
    description: Mapped[str] = mapped_column(Text, nullable=True) # Descripción del planeta
    gravity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Clave foránea: Un planeta puede ser un favorito
    favorites = relationship('Favorites', back_populates='planets') 
    

    def serialize(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "description": self.description,
            "gravity": self.gravity,
        }

class Favorites(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='favorites') # Relación inversa a User

    character_id: Mapped[int] = mapped_column(ForeignKey('characters.id'), nullable=False)
    characters = relationship('Characters', back_populates='favorites') # Relación inversa a Character

    planets_id: Mapped[int] = mapped_column(ForeignKey('planets.id'), nullable=False)
    planets = relationship('Planets', back_populates='favorites') # Relación inversa a Character


    def __repr__(self):
        return f'<Favorite {self.id} by User {self.user_id} on Character {self.character_id}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.content_id,
            "planets_id": self.planets_id
        }

