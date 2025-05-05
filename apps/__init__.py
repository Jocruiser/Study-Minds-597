# apps/__init__.py
# dir is treated as a package 
# defines a function that will create and configure the app
# initializes the app and loads the db, secret key
from flask import Flask
from flask_login import LoginManager
#from .models import db  # Importing db object from models.py
from dotenv import load_dotenv
import os
from .models import User
from .db import db # imports db from db.py

# Initialize login manager
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    # Create the Flask app instance
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Load environment variables from .env
    load_dotenv()
    app.secret_key = os.getenv('SECRET_KEY')  # Secret key for sessions
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database and login manager
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .routes import auth
    # Register the auth blueprint (the routes)
    app.register_blueprint(auth)

    return app
