"""
Entry/Check-in Blueprint
- Handles user check-in via QR code
- Validates users against registration database
- Enforces one check-in per day limit
- CRITICAL: No entry without prior registration
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from models import db, User, EntryLog
from datetime import datetime, date

entry_bp = Blueprint('entry', __name__)


@entry_bp.route('/', methods=['GET', 'POST'])
def verify_entry():
    """
    Handle user entry/check-in verification
    - GET: Display entry verification form
    - POST: Process entry verification
    
    CRITICAL VALIDATION:
    - User must exist in registered users table
    - User can only check in once per day
    - Mobile number OR Membership ID required
    """
    if request.method == 'POST':
        try:
            # Extract form data - User provides either mobile or membership ID
            mobile_number = request.form.get('mobile_number', '').strip()
            membership_id = request.form.get('membership_id', '').strip()
            
            # ============= VALIDATION =============
            
            # User must provide at least one identifier
            if not mobile_number and not membership_id:
                flash('Please enter either Mobile Number or Membership ID', 'error')
                return redirect(url_for('entry.verify_entry'))
            
            # ============= DATABASE LOOKUP =============
            
            # Search for user in database
            user = None
            
            if mobile_number:
                # Search by mobile number
                user = User.query.filter_by(mobile_number=mobile_number).first()
            elif membership_id:
                # Search by membership ID
                user = User.query.filter_by(membership_id=membership_id).first()
            
            # CRITICAL: If user not found, reject entry
            if not user:
                flash('User Not Found / Not Registered. Please register first.', 'error')
                return redirect(url_for('entry.verify_entry'))
            
            # ============= DAILY CHECK-IN LIMIT =============
            
            # Check if user already checked in today
            today = date.today()
            existing_entry = EntryLog.query.filter(
                EntryLog.user_id == user.id,
                EntryLog.entry_date == today
            ).first()
            
            if existing_entry:
                flash(f'Already Checked In Today! Welcome back, {user.name}.', 'warning')
                return redirect(url_for('entry.verify_entry'))
            
            # ============= CREATE ENTRY LOG =============
            
            # Create new entry log record
            entry_log = EntryLog(
                user_id=user.id,
                entry_date=today,
                entry_time=datetime.utcnow()
            )
            
            # Add to database and commit
            db.session.add(entry_log)
            db.session.commit()
            
            # Success response
            flash(f'✓ Entry Successful! Welcome {user.name}. Membership: {user.membership_id}', 'success')
            return redirect(url_for('entry.verify_entry'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Entry failed: {str(e)}', 'error')
            return redirect(url_for('entry.verify_entry'))
    
    # GET request - display entry verification form
    return render_template('entry.html')


@entry_bp.route('/qr')
def qr_display():
    """
    Display entry/check-in QR code
    - QR code is permanent and never expires
    - Points to the entry verification endpoint
    - Multiple users can scan it
    """
    from utils import QRCodeGenerator
    
    # Generate QR code for entry endpoint
    qr_code = QRCodeGenerator.generate_entry_qr('http://localhost:5000')
    
    return render_template('qr_display.html',
                         qr_code=qr_code,
                         qr_type='Entry/Check-in',
                         description='Scan this QR code to check in to the gym')


@entry_bp.route('/api/check-duplicate', methods=['POST'])
def check_duplicate():
    """
    API endpoint to check if a user exists (used for form validation)
    Returns JSON response with user status
    """
    data = request.get_json()
    mobile_number = data.get('mobile_number', '').strip()
    membership_id = data.get('membership_id', '').strip()
    
    user = None
    if mobile_number:
        user = User.query.filter_by(mobile_number=mobile_number).first()
    elif membership_id:
        user = User.query.filter_by(membership_id=membership_id).first()
    
    if user:
        # Check if already entered today
        today = date.today()
        already_entered = EntryLog.query.filter(
            EntryLog.user_id == user.id,
            EntryLog.entry_date == today
        ).first()
        
        return jsonify({
            'exists': True,
            'name': user.name,
            'membership_id': user.membership_id,
            'already_entered_today': bool(already_entered)
        })
    
    return jsonify({'exists': False})
