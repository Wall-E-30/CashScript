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
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Cascading relationships for clean deletions
    members = db.relationship('GroupMember', backref='group', lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship('GroupExpense', backref='group', lazy=True, cascade="all, delete-orphan")
    settlements = db.relationship('Settlement', backref='group', lazy=True, cascade="all, delete-orphan")

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(50), default='member')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class GroupExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    paid_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    splits = db.relationship('ExpenseSplit', backref='expense', lazy=True, cascade="all, delete-orphan")

class ExpenseSplit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('group_expense.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owed_amount = db.Column(db.Float, nullable=False)
    split_type = db.Column(db.String(50), default='equal') # Supports equal, exact, or percentage

class Settlement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    settled_at = db.Column(db.DateTime, default=datetime.utcnow)