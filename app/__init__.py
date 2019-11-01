from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(db_file='sqlite:////tmp/proj.db'):
    """Construct the core application."""
    app = Flask(__name__)
    db.init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_file

    with app.app_context():
        # Imports
        from . import routes

        # Create tables for our models
        db.create_all()

        return app

