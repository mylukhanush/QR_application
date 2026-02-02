"""
Registration Blueprint
- Handles user registration via QR code
- Prevents duplicate mobile numbers
- Auto-generates unique membership IDs
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models import db, User
from datetime import datetime
import secrets

registration_bp = Blueprint('registration', __name__)


def generate_membership_id():
    """
    Generate unique membership ID in format: MEM-XXXXX
    - Checks database to ensure uniqueness
    """
    while True:
        # Generate 5-digit random number
        random_id = secrets.randbelow(100000)
        membership_id = f'MEM-{random_id:05d}'
        
        # Check if ID already exists in database
        if not User.query.filter_by(membership_id=membership_id).first():
            return membership_id


@registration_bp.route('/', methods=['GET', 'POST'])
def register():
    """
    Handle user registration
    - GET: Display registration form
    - POST: Process registration form submission
    
    Validation:
    - Mobile number must be unique (checked against database)
    - Age must be valid
    - All fields required
    """
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.form.get('name', '').strip()
            age_str = request.form.get('age', '').strip()
            mobile_number = request.form.get('mobile_number', '').strip()
            
            # ============= VALIDATION =============
            
            # Validate name
            if not name or len(name) < 2:
                flash('Name must be at least 2 characters long', 'error')
                return redirect(url_for('registration.register'))
            
            # Validate age
            if not age_str or not age_str.isdigit():
                flash('Age must be a valid number', 'error')
                return redirect(url_for('registration.register'))
            
            age = int(age_str)
            if age < 10 or age > 120:
                flash('Age must be between 10 and 120', 'error')
                return redirect(url_for('registration.register'))
            
            # Validate mobile number
            if not mobile_number or len(mobile_number) < 10:
                flash('Mobile number must be at least 10 digits', 'error')
                return redirect(url_for('registration.register'))
            
            # CRITICAL: Check if mobile number already exists
            # This ensures no duplicate registrations with same phone
            existing_user = User.query.filter_by(mobile_number=mobile_number).first()
            if existing_user:
                flash('This mobile number is already registered. Please use a different number.', 'error')
                return redirect(url_for('registration.register'))
            
            # ============= USER CREATION =============
            
            # Generate unique membership ID
            membership_id = generate_membership_id()
            
            # Create new user object
            new_user = User(
                name=name,
                age=age,
                mobile_number=mobile_number,
                membership_id=membership_id,
                registration_date=datetime.utcnow()
            )
            
            # Add to database and commit
            db.session.add(new_user)
            db.session.commit()
            
            # Success response
            flash(f'Registration successful! Your Membership ID: {membership_id}', 'success')
            return redirect(url_for('registration.register'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect(url_for('registration.register'))
    
    # GET request - display registration form
    return render_template('registration.html')


@registration_bp.route('/qr')
def qr_display():
    """
    Display registration QR code
    - QR code is permanent and never expires
    - Points to the registration endpoint
    - Multiple users can scan it
    """
    from utils import QRCodeGenerator
    from config import APP_CONFIG
    
    # Generate QR code for registration endpoint
    qr_code = QRCodeGenerator.generate_registration_qr('http://localhost:5000')
    
    return render_template('qr_display.html', 
                         qr_code=qr_code,
                         qr_type='Registration',
                         description='Scan this QR code to register as a gym member')
