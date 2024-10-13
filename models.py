from app import db
from datetime import datetime

class UserRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    sponsor_email = db.Column(db.String(100), nullable=False)
    magic = db.Column(db.String(100))
    post_url = db.Column(db.String(200))
    user_ip = db.Column(db.String(50))
    user_mac = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(200))
