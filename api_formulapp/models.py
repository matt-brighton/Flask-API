from . import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    created_date = db.Column(db.DateTime(timezone=True), default=func.now())
    favourite_team = db.Column(db.String(50))
    favourite_driver = db.Column(db.String(50))
