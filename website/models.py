from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
from website.extensions import db, login_manager

# db = SQLAlchemy()   #Creating an instance
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True, nullable = False)
    password_hash = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(200))
    transactions = db.relationship('Transaction' , backref = 'user', lazy = True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = True)
    type = db.Column(db.String(20), nullable =False)
    description = db.Column(db.String(200))
    transactions = db.relationship('Transaction', backref = 'category', lazy = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('categories', lazy=True))

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable = False)
    date = db.Column(db.DateTime(timezone = True),
                     default = lambda: datetime.now(timezone.utc)
                     ) #Storing date and time
    payment_mode = db.Column(db.String(25), nullable = False)   #How was the payment executed
    type = db.Column(db.String(10), nullable=False)
    # Foregin Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))   #Only the user which addwd expense can see/modify it
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))   #To identify expenditure's type

