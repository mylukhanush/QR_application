from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models import User, EntryLog, db
from functools import wraps
from datetime import date, datetime

admin_bp = Blueprint('admin', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    filter_date_str = request.args.get('date')
    
    if filter_date_str:
        try:
            filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
        except ValueError:
            filter_date = today
    else:
        filter_date = today

    # Stats
    total_registrations = User.query.count()
    daily_entry_count = EntryLog.query.filter_by(entry_date=filter_date).count()
    
    # Lists
    entries_today = EntryLog.query.filter_by(entry_date=filter_date).all()
    entered_user_ids = [entry.user_id for entry in entries_today]
    
    # Users who have NOT entered today
    # Note: For large databases, fetching all users might be slow. 
    # But for a gym/org with <1000s users, this is fine.
    # A more optimized query would be LEFT JOIN where entry is NULL.
    # user_query = db.session.query(User).outerjoin(EntryLog, (User.id == EntryLog.user_id) & (EntryLog.entry_date == filter_date))
    # not_entered_today = user_query.filter(EntryLog.id == None).all()
    
    # Doing Python-side filtering for simplicity and readability as requested, 
    # unless dataset is huge. Let's do SQL query for best practice.
    subquery = db.session.query(EntryLog.user_id).filter(EntryLog.entry_date == filter_date).subquery()
    not_entered_today = User.query.filter(~User.id.in_(subquery)).all()
    
    return render_template('admin_dashboard.html', 
                           total_registrations=total_registrations,
                           daily_entry_count=daily_entry_count,
                           entries_today=entries_today,
                           not_entered_today=not_entered_today,
                           filter_date=filter_date)

@admin_bp.route('/qr')
@login_required
def view_qr_codes():
    return render_template('qr_view.html')

@admin_bp.route('/users')
@login_required
def all_users():
    users = User.query.all()
    return render_template('all_users.html', users=users)
