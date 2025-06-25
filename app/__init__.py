from flask import Flask
from app.db import init_db

def create_app():
    app = Flask(__name__)
    app.secret_key = 'supersecretkey'  #

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
