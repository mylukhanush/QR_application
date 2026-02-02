from flask import Flask
from config import APP_CONFIG
from app.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(APP_CONFIG)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register Blueprints
    from app.main_routes import main_bp
    from app.admin_routes import admin_bp
    from app.auth_routes import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
    return app
