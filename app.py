"""
Gym QR Code Application - Main Flask Application
================================================

A complete QR code-based gym membership and attendance tracking system.

FEATURES:
1. User Registration via QR code with auto-generated membership IDs
2. Check-in/Entry system with one-per-day validation
3. Admin dashboard with member and entry logs
4. Session-based admin authentication
5. SQLAlchemy ORM with MySQL database
6. Role-based access control

ARCHITECTURE:
- Flask with Blueprint architecture
- SQLAlchemy for database ORM
- Jinja2 templates for HTML rendering
- Pure CSS styling (no JavaScript required)
- QR code generation with qrcode library
"""

from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig
from models import db
from routes_registration import registration_bp
from routes_entry import entry_bp
from routes_admin import admin_bp
import os
from datetime import timedelta


def create_app(config=None):
    """
    Application factory function to create and configure Flask app
    
    Args:
        config: Configuration object (defaults to DevelopmentConfig)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        config = DevelopmentConfig()
    app.config.from_object(config)
    
    # Initialize database
    db.init_app(app)
    
    # Configure session
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True for HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Register blueprints
    # ============================================================
    # Registration Blueprint: /register
    # - User registration form
    # - Registration QR code display
    app.register_blueprint(registration_bp, url_prefix='/register')
    
    # Entry/Check-in Blueprint: /entry
    # - Entry verification form
    # - Entry QR code display
    # - Daily check-in limit enforcement
    app.register_blueprint(entry_bp, url_prefix='/entry')
    
    # Admin Blueprint: /admin
    # - Admin login/logout
    # - Dashboard with statistics
    # - View all members
    # - View entry logs
    # - View users not entered today
    # - Detailed statistics
    app.register_blueprint(admin_bp)
    
    # ============================================================
    # HOME ROUTE
    # ============================================================
    @app.route('/')
    def index():
        """
        Home page showing application overview
        Links to registration, check-in, and admin panel
        """
        return render_template('index.html')
    
    # ============================================================
    # ERROR HANDLERS
    # ============================================================
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors"""
        return render_template('500.html'), 500
    
    # ============================================================
    # DATABASE INITIALIZATION
    # ============================================================
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("✓ Database tables initialized")
    
    return app


if __name__ == '__main__':
    """
    Application entry point
    
    Before running:
    1. Install dependencies: pip install -r requirements.txt
    2. Configure MySQL database in config.py
    3. Update admin credentials in config.py (ADMIN_USERNAME, ADMIN_PASSWORD)
    4. Run: python app.py
    
    The application will be available at: http://localhost:5000
    """
    
    # Create Flask app
    app = create_app()
    
    # Run development server
    app.run(
        host='localhost',
        port=5000,
        debug=True,
        use_reloader=True
    )
