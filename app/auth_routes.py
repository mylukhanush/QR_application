from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask import current_app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == current_app.config['ADMIN_USERNAME'] and password == current_app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials', 'error')
            
    return render_template('admin_login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('auth.login'))
