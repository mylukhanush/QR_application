"""
SQLAlchemy database models for the Gym QR Application
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Index

db = SQLAlchemy()


class User(db.Model):
    """
    User model for storing registered gym members
    - UNIQUE constraint on mobile_number to prevent duplicate registrations
    - auto-incremented membership_id is unique
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # User information
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    mobile_number = db.Column(db.String(15), unique=True, nullable=False, index=True)
    
    # Auto-generated unique membership ID (format: MEM-XXXXX)
    membership_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Timestamps
    registration_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to EntryLog
    entry_logs = db.relationship('EntryLog', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.membership_id} - {self.name}>'

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'mobile_number': self.mobile_number,
            'membership_id': self.membership_id,
            'registration_date': self.registration_date.strftime('%Y-%m-%d %H:%M:%S')
        }


class EntryLog(db.Model):
    """
    EntryLog model for tracking user check-ins
    - Records when a user enters the gym
    - One entry per user per day is allowed
    - Indexed by user_id and entry_date for quick lookups
    """
    __tablename__ = 'entry_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to User table
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Entry information
    entry_date = db.Column(db.Date, nullable=False, index=True)  # Date only for daily check
    entry_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Exit information (optional, for future use)
    exit_time = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Composite index for quick lookup of user entry on specific date
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'entry_date'),
    )

    def __repr__(self):
        return f'<EntryLog User {self.user_id} - {self.entry_date}>'

    def to_dict(self):
        """Convert entry log object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name,
            'membership_id': self.user.membership_id,
            'mobile_number': self.user.mobile_number,
            'entry_date': self.entry_date.strftime('%Y-%m-%d'),
            'entry_time': self.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
            'exit_time': self.exit_time.strftime('%Y-%m-%d %H:%M:%S') if self.exit_time else None
        }
