"""
Database Setup Script
====================

This script initializes the MySQL database for the Gym QR Application.

IMPORTANT: Run this script BEFORE running the Flask application.

Setup Steps:
1. Install MySQL
2. Create a MySQL user and database
3. Update config.py with your database credentials
4. Run this script: python database_setup.py
"""

import sys
from app import create_app, db
from models import User, EntryLog


def setup_database():
    """
    Initialize the database with proper tables and indexes
    """
    try:
        # Create Flask app context
        app = create_app()
        
        with app.app_context():
            print("=" * 60)
            print("Database Setup - Gym QR Application")
            print("=" * 60)
            
            # Drop existing tables (optional - comment out if you want to keep data)
            # db.drop_all()
            # print("✓ Dropped existing tables")
            
            # Create all tables
            db.create_all()
            print("✓ Created database tables:")
            print("  - users")
            print("  - entry_logs")
            
            # Print table structure information
            print("\n" + "=" * 60)
            print("Database Schema")
            print("=" * 60)
            
            print("\nTable: users")
            print("  - id (Primary Key, AUTO_INCREMENT)")
            print("  - name (VARCHAR 100, NOT NULL)")
            print("  - age (INT, NOT NULL)")
            print("  - mobile_number (VARCHAR 15, UNIQUE, NOT NULL, INDEX)")
            print("  - membership_id (VARCHAR 20, UNIQUE, NOT NULL, INDEX)")
            print("  - registration_date (DATETIME, DEFAULT NOW)")
            print("  - updated_at (DATETIME, DEFAULT NOW)")
            
            print("\nTable: entry_logs")
            print("  - id (Primary Key, AUTO_INCREMENT)")
            print("  - user_id (Foreign Key -> users.id)")
            print("  - entry_date (DATE, NOT NULL, INDEX)")
            print("  - entry_time (DATETIME, DEFAULT NOW)")
            print("  - exit_time (DATETIME, NULL)")
            print("  - created_at (DATETIME, DEFAULT NOW)")
            print("  - Composite Index: (user_id, entry_date)")
            
            print("\n" + "=" * 60)
            print("✓ Database initialization complete!")
            print("=" * 60)
            print("\nApplication is ready to run.")
            print("Start with: python app.py")
            
    except Exception as e:
        print(f"✗ Error during database setup: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure MySQL is running")
        print("2. Check database credentials in config.py")
        print("3. Verify database exists or is creatable by the user")
        sys.exit(1)


if __name__ == '__main__':
    setup_database()
