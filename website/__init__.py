from flask import Flask
from config import Config
from .extensions import db, mail, login_manager
from flask_migrate import Migrate

migrate = Migrate()  # 1. Initialize the Migrate object here

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    migrate.init_app(app, db)  # 2. Bind Migrate to your app and database

    # Register Blueprints (Routes)
    from .routes import main
    app.register_blueprint(main)

    # Create Database Tables
    # from .models import User, Category, Transaction
    # with app.app_context():
    #     db.create_all()

    return app