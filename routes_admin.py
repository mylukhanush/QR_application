"""
Admin Blueprint
- Admin panel with session-based authentication
- View all registered users
- View entry logs with daily statistics
- Filter by date
- Dashboard with key metrics
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from models import db, User, EntryLog
from datetime import datetime, date, timedelta
from config import APP_CONFIG
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def login_required(f):
    """
    Decorator to check if user is authenticated as admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Admin login page
    - Session-based authentication
    - Credentials stored in config (should be environment variables in production)
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validate credentials against config
        if (username == APP_CONFIG.ADMIN_USERNAME and 
            password == APP_CONFIG.ADMIN_PASSWORD):
            
            # Create session
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session.permanent = True
            
            flash('Login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('admin.login'))
    
    return render_template('admin_login.html')


@admin_bp.route('/logout')
def logout():
    """
    Admin logout
    - Clear session
    """
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Admin dashboard
    - View key statistics
    - Total registered users
    - Daily entry count
    - Users entered today
    - Users not entered today
    """
    # Get statistics
    total_users = User.query.count()
    
    today = date.today()
    users_entered_today = db.session.query(User).join(EntryLog).filter(
        EntryLog.entry_date == today
    ).count()
    
    users_not_entered_today = total_users - users_entered_today
    
    # Get recent registrations (last 5)
    recent_registrations = User.query.order_by(User.registration_date.desc()).limit(5).all()
    
    # Get today's entries
    today_entries = EntryLog.query.filter(
        EntryLog.entry_date == today
    ).order_by(EntryLog.entry_time.desc()).all()
    
    stats = {
        'total_users': total_users,
        'users_entered_today': users_entered_today,
        'users_not_entered_today': users_not_entered_today,
        'today_entry_count': len(today_entries)
    }
    
    return render_template('admin_dashboard.html',
                         stats=stats,
                         recent_registrations=recent_registrations,
                         today_entries=today_entries)


@admin_bp.route('/users')
@login_required
def view_users():
    """
    View all registered users
    - Pagination support
    - Search by name or mobile number
    """
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    
    query = User.query
    
    # Search functionality
    if search_query:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{search_query}%'),
                User.mobile_number.ilike(f'%{search_query}%'),
                User.membership_id.ilike(f'%{search_query}%')
            )
        )
    
    # Pagination
    users = query.order_by(User.registration_date.desc()).paginate(
        page=page,
        per_page=APP_CONFIG.ITEMS_PER_PAGE
    )
    
    return render_template('admin_users.html',
                         users=users,
                         search_query=search_query)


@admin_bp.route('/entries')
@login_required
def view_entries():
    """
    View entry logs
    - Filter by date
    - Pagination support
    """
    page = request.args.get('page', 1, type=int)
    date_filter = request.args.get('date', '').strip()
    
    query = EntryLog.query
    
    # Date filter
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(EntryLog.entry_date == filter_date)
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD', 'error')
    else:
        # Default: show today's entries
        filter_date = date.today()
        query = query.filter(EntryLog.entry_date == filter_date)
    
    # Pagination
    entries = query.order_by(EntryLog.entry_time.desc()).paginate(
        page=page,
        per_page=APP_CONFIG.ITEMS_PER_PAGE
    )
    
    return render_template('admin_entries.html',
                         entries=entries,
                         date_filter=date_filter or date.today().strftime('%Y-%m-%d'))


@admin_bp.route('/entries-today-not-entered')
@login_required
def view_users_not_entered():
    """
    View users who have NOT entered today
    """
    today = date.today()
    
    # Get users who haven't entered today using subquery
    users_entered_today = db.session.query(EntryLog.user_id).filter(
        EntryLog.entry_date == today
    ).distinct()
    
    users_not_entered = User.query.filter(
        ~User.id.in_(users_entered_today)
    ).order_by(User.name).all()
    
    return render_template('admin_not_entered.html',
                         users_not_entered=users_not_entered,
                         date=today.strftime('%Y-%m-%d'))


@admin_bp.route('/statistics')
@login_required
def statistics():
    """
    Detailed statistics page
    - Daily entry trends
    - Registration trends
    - Top entry days
    """
    # Get last 7 days of data
    today = date.today()
    seven_days_ago = today - timedelta(days=7)
    
    # Daily entry counts for last 7 days
    daily_stats = db.session.query(
        EntryLog.entry_date,
        db.func.count(EntryLog.id).label('entry_count')
    ).filter(
        EntryLog.entry_date >= seven_days_ago
    ).group_by(
        EntryLog.entry_date
    ).order_by(
        EntryLog.entry_date.desc()
    ).all()
    
    # Registration stats for last 7 days
    registration_stats = db.session.query(
        db.func.date(User.registration_date).label('reg_date'),
        db.func.count(User.id).label('count')
    ).filter(
        User.registration_date >= seven_days_ago
    ).group_by(
        db.func.date(User.registration_date)
    ).order_by(
        db.func.date(User.registration_date).desc()
    ).all()
    
    return render_template('admin_statistics.html',
                         daily_stats=daily_stats,
                         registration_stats=registration_stats)


@admin_bp.route('/api/user/<int:user_id>')
@login_required
def get_user_details(user_id):
    """
    API endpoint to get user details with entry history
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get all entries for this user
    entries = EntryLog.query.filter_by(user_id=user_id).order_by(
        EntryLog.entry_date.desc()
    ).all()
    
    return jsonify({
        'user': user.to_dict(),
        'entries': [entry.to_dict() for entry in entries],
        'total_entries': len(entries)
    })
