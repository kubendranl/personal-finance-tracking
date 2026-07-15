from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    financial_records = db.relationship('FinancialRecord', backref='user', lazy=True)

class FinancialRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Income & Basics
    monthly_income = db.Column(db.Float, nullable=False)
    total_savings = db.Column(db.Float, nullable=False, default=0.0) # Existing savings
    monthly_savings = db.Column(db.Float, nullable=False, default=0.0) # Monthly contribution
    total_debt = db.Column(db.Float, nullable=False, default=0.0)
    
    # Expenses breakdown
    housing_rent = db.Column(db.Float, nullable=False, default=0.0)
    food_dining = db.Column(db.Float, nullable=False, default=0.0)
    transportation = db.Column(db.Float, nullable=False, default=0.0)
    utilities = db.Column(db.Float, nullable=False, default=0.0)
    entertainment = db.Column(db.Float, nullable=False, default=0.0)
    miscellaneous = db.Column(db.Float, nullable=False, default=0.0)
