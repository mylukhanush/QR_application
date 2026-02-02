from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import db, User, EntryLog
from datetime import datetime, date
import uuid

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('base.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        try:
            age = int(request.form.get('age'))
        except (ValueError, TypeError):
            flash('Invalid age', 'error')
            return redirect(url_for('main.register'))
            
        mobile = request.form.get('mobile')
        
        # Validation
        if User.query.filter_by(mobile_number=mobile).first():
            flash('Mobile number already registered!', 'error')
            return redirect(url_for('main.register'))
            
        # Generate Membership ID
        # Format: MEM-{mobile_last_4}-{random_4} for uniqueness and simplicity
        # Or just UUID. Let's use a simpler readable format as requested "MEM-XXXXX"
        import random
        rand_suffix = ''.join(random.choices('0123456789', k=5))
        membership_id = f"MEM-{rand_suffix}"
        
        # Ensure it's unique (simple collision check)
        while User.query.filter_by(membership_id=membership_id).first():
            rand_suffix = ''.join(random.choices('0123456789', k=5))
            membership_id = f"MEM-{rand_suffix}"
            
        new_user = User(name=name, age=age, mobile_number=mobile, membership_id=membership_id)
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'Registration Successful! Your Membership ID is {membership_id}', 'success')
        return redirect(url_for('main.register')) # Stay on page or go somewhere? Requirement: "Registration QR code must NEVER expire" implies we probably just show success on the same device and let next person scan. 
        # But usually user scans on THEIR phone. So we show success page.
        
    return render_template('register.html')

@main_bp.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        identifier = request.form.get('identifier') # Mobile or Membership ID
        
        user = User.query.filter(
            (User.mobile_number == identifier) | (User.membership_id == identifier)
        ).first()
        
        if not user:
            flash('User Not Found / Not Registered', 'error')
            return redirect(url_for('main.checkin'))
            
        # Check if already entered today
        today = date.today()
        existing_entry = EntryLog.query.filter_by(user_id=user.id, entry_date=today).first()
        
        if existing_entry:
            flash(f'User {user.name} already checked in today at {existing_entry.entry_time.strftime("%H:%M:%S")}', 'warning')
            return redirect(url_for('main.checkin'))
            
        # Create Entry
        new_entry = EntryLog(user_id=user.id, entry_date=today)
        db.session.add(new_entry)
        db.session.commit()
        
        flash(f'Welcome, {user.name}! Check-in Successful.', 'success')
        return redirect(url_for('main.checkin'))
        
    return render_template('checkin.html')
