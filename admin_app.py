"""
Separate Admin Application for EnergyTrack
Runs on port 5001 - Completely isolated from user application
"""
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail
from models.database import db, User, Payment, SupportTicket, ConsumptionLog
from config import Config
from datetime import datetime, timedelta
from utils.timezone_utils import get_ist_now
from sqlalchemy import func
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Admin authentication required'
login_manager.login_message_category = 'danger'

# Initialize Flask-Mail
mail = Mail()
try:
    mail.init_app(app)
except:
    print("Warning: Flask-Mail not configured. Email features disabled.")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_admin:
            login_user(user, remember=True)
            flash('Welcome to Admin Portal!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials or not an admin account', 'danger')
    
    return render_template('admin/admin_login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout admin"""
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('admin_login'))


# ============================================================
# DASHBOARD
# ============================================================

@app.route('/')
@app.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with analytics"""
    # User statistics (excluding admins)
    total_users = User.query.filter_by(is_admin=False).count()
    free_users = User.query.filter_by(plan_type='FREE', is_admin=False).count()
    premium_users = User.query.filter(User.plan_type.in_(['PREMIUM_MONTHLY', 'PREMIUM_YEARLY']), User.is_admin == False).count()
    trial_users = User.query.filter(User.trial_ends_at > get_ist_now(), User.is_admin == False).count()
    
    # Revenue statistics
    total_payments = Payment.query.filter_by(status='SUCCESS').count()
    total_revenue = db.session.query(func.sum(Payment.amount)).filter_by(status='SUCCESS').scalar() or 0
    
    # Monthly revenue (last 30 days)
    thirty_days_ago = get_ist_now() - timedelta(days=30)
    monthly_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'SUCCESS',
        Payment.created_at >= thirty_days_ago
    ).scalar() or 0
    
    # Support tickets
    open_tickets = SupportTicket.query.filter_by(status='open').count()
    total_tickets = SupportTicket.query.count()
    
    # Recent users (last 10)
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Revenue breakdown
    monthly_revenue_count = Payment.query.filter_by(plan_type='PREMIUM_MONTHLY', status='SUCCESS').count()
    yearly_revenue_count = Payment.query.filter_by(plan_type='PREMIUM_YEARLY', status='SUCCESS').count()
    
    stats = {
        'total_users': total_users,
        'free_users': free_users,
        'premium_users': premium_users,
        'trial_users': trial_users,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'total_payments': total_payments,
        'open_tickets': open_tickets,
        'total_tickets': total_tickets,
        'monthly_subs': monthly_revenue_count,
        'yearly_subs': yearly_revenue_count,
        'recent_users': recent_users
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         open_tickets_count=open_tickets,
                         current_time=get_ist_now().strftime('%d %b %Y, %I:%M %p IST'))


# ============================================================
# USER MANAGEMENT
# ============================================================

@app.route('/users')
@login_required
@admin_required
def users():
    """User management"""
    all_users = User.query.order_by(User.created_at.desc()).all()
    open_tickets_count = SupportTicket.query.filter_by(status='open').count()
    return render_template('admin/users.html', users=all_users, open_tickets_count=open_tickets_count)


@app.route('/user/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View user details"""
    user = User.query.get_or_404(user_id)
    payments = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
    tickets = SupportTicket.query.filter_by(user_id=user_id).order_by(SupportTicket.created_at.desc()).all()
    open_tickets_count = SupportTicket.query.filter_by(status='open').count()
    
    return render_template('admin/user_detail.html', user=user, payments=payments, tickets=tickets, open_tickets_count=open_tickets_count)


@app.route('/user/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot modify your own admin status', 'warning')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Admin status {"enabled" if user.is_admin else "disabled"} for {user.name}', 'success')
    
    return redirect(url_for('user_detail', user_id=user_id))


@app.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user and all associated data"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('users'))
    
    if user.is_admin:
        flash('Cannot delete admin accounts', 'danger')
        return redirect(url_for('users'))
    
    # Delete associated data
    Payment.query.filter_by(user_id=user_id).delete()
    SupportTicket.query.filter_by(user_id=user_id).delete()
    ConsumptionLog.query.filter_by(user_id=user_id).delete()
    
    # Delete user
    user_name = user.name
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User "{user_name}" and all associated data deleted successfully', 'success')
    return redirect(url_for('users'))


# ============================================================
# SUPPORT TICKETS
# ============================================================

@app.route('/tickets')
@login_required
@admin_required
def tickets():
    """View all support tickets"""
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        all_tickets = SupportTicket.query.order_by(SupportTicket.created_at.desc()).all()
    else:
        all_tickets = SupportTicket.query.filter_by(status=status_filter).order_by(SupportTicket.created_at.desc()).all()
    
    open_tickets_count = SupportTicket.query.filter_by(status='open').count()
    return render_template('admin/tickets.html', tickets=all_tickets, status_filter=status_filter, open_tickets_count=open_tickets_count)


@app.route('/ticket/<int:ticket_id>/reply', methods=['POST'])
@login_required
@admin_required
def reply_ticket(ticket_id):
    """Reply to a support ticket"""
    ticket = SupportTicket.query.get_or_404(ticket_id)
    reply = request.form.get('reply')
    
    if reply:
        ticket.admin_reply = reply
        ticket.status = 'closed'
        ticket.updated_at = get_ist_now()
        db.session.commit()
        
        flash('Reply sent successfully', 'success')
    
    return redirect(url_for('tickets'))


@app.route('/ticket/<int:ticket_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_ticket_status(ticket_id):
    """Update ticket status"""
    ticket = SupportTicket.query.get_or_404(ticket_id)
    new_status = request.form.get('status')
    
    if new_status in ['open', 'in_progress', 'closed']:
        ticket.status = new_status
        ticket.updated_at = get_ist_now()
        db.session.commit()
        flash(f'Ticket status updated to {new_status}', 'success')
    
    return redirect(url_for('tickets'))


# ============================================================
# REVENUE ANALYTICS
# ============================================================

@app.route('/revenue')
@login_required
@admin_required
def revenue():
    """Revenue analytics"""
    all_payments = Payment.query.filter_by(status='SUCCESS').order_by(Payment.created_at.desc()).all()
    
    # Calculate totals
    total_revenue = sum(p.amount for p in all_payments)
    monthly_total = sum(p.amount for p in all_payments if p.plan_type == 'PREMIUM_MONTHLY')
    yearly_total = sum(p.amount for p in all_payments if p.plan_type == 'PREMIUM_YEARLY')
    
    revenue_stats = {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_total,
        'yearly_revenue': yearly_total,
        'total_transactions': len(all_payments),
        'payments': all_payments
    }
    
    open_tickets_count = SupportTicket.query.filter_by(status='open').count()
    
    return render_template('admin/revenue.html', stats=revenue_stats, open_tickets_count=open_tickets_count)


# ============================================================
# SYSTEM SETTINGS
# ============================================================

@app.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """System settings"""
    if request.method == 'POST':
        # Update email settings
        new_admin_email = request.form.get('admin_email')
        mail_username = request.form.get('mail_username')
        mail_password = request.form.get('mail_password')
        mail_server = request.form.get('mail_server')
        mail_port = request.form.get('mail_port')
        
        # Update runtime config
        if new_admin_email:
            app.config['ADMIN_EMAIL'] = new_admin_email
        if mail_username:
            app.config['MAIL_USERNAME'] = mail_username
        if mail_password:
            app.config['MAIL_PASSWORD'] = mail_password
        if mail_server:
            app.config['MAIL_SERVER'] = mail_server
        if mail_port:
            app.config['MAIL_PORT'] = int(mail_port)
        
        # Save to .env file for persistence
        try:
            import os
            env_path = os.path.join(os.path.dirname(__file__), '.env')
            env_lines = []
            
            # Read existing .env or create new
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_lines = f.readlines()
            
            # Update or add settings
            settings_to_update = {}
            if new_admin_email:
                settings_to_update['ADMIN_EMAIL'] = new_admin_email
            if mail_username:
                settings_to_update['MAIL_USERNAME'] = mail_username
            if mail_password:
                settings_to_update['MAIL_PASSWORD'] = mail_password
            if mail_server:
                settings_to_update['MAIL_SERVER'] = mail_server
            if mail_port:
                settings_to_update['MAIL_PORT'] = mail_port
            
            # Update existing lines or prepare new ones
            updated_keys = set()
            new_lines = []
            
            for line in env_lines:
                stripped = line.strip()
                if '=' in stripped and not stripped.startswith('#'):
                    key = stripped.split('=')[0].strip()
                    if key in settings_to_update:
                        new_lines.append(f'{key}={settings_to_update[key]}\n')
                        updated_keys.add(key)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            # Add new settings that weren't in the file
            for key, value in settings_to_update.items():
                if key not in updated_keys:
                    new_lines.append(f'{key}={value}\n')
            
            # Write back to .env
            with open(env_path, 'w') as f:
                f.writelines(new_lines)
            
            # Reinitialize Flask-Mail with new settings
            try:
                global mail
                mail.init_app(app)
                print("[SUCCESS] Email configuration updated and Flask-Mail reinitialized")
            except Exception as mail_error:
                print(f"[WARNING] Failed to reinitialize Flask-Mail: {mail_error}")
            
            flash('Settings saved successfully! Changes will take effect immediately.', 'success')
        except Exception as e:
            flash(f'Settings updated in memory but failed to save to .env: {str(e)}', 'warning')
        
        return redirect(url_for('settings'))
    
    open_tickets_count = SupportTicket.query.filter_by(status='open').count()
    return render_template('admin/settings.html', open_tickets_count=open_tickets_count, config=app.config)


# ============================================================
# ADMIN PROFILE
# ============================================================

@app.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_profile():
    """Admin profile management"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_name':
            new_name = request.form.get('name')
            if new_name:
                current_user.name = new_name
                db.session.commit()
                flash('Name updated successfully', 'success')
        
        elif action == 'update_email':
            new_email = request.form.get('email')
            current_password = request.form.get('current_password')
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
            elif User.query.filter_by(email=new_email).first():
                flash('Email already in use', 'danger')
            else:
                current_user.email = new_email
                db.session.commit()
                flash('Email updated successfully', 'success')
        
        elif action == 'update_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'danger')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters', 'danger')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password updated successfully', 'success')
        
        return redirect(url_for('admin_profile'))
    
    open_tickets_count = SupportTicket.query.filter_by(status='open').count()
    return render_template('admin/profile.html', open_tickets_count=open_tickets_count)


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        admin_email = app.config.get('ADMIN_EMAIL')
        admin_password = app.config.get('ADMIN_PASSWORD')

        # Create admin account only when explicit credentials are configured.
        if admin_email and admin_password:
            admin = User.query.filter_by(email=admin_email).first()
            if not admin:
                admin = User(
                    name='System Administrator',
                    email=admin_email,
                    is_admin=True,
                    is_verified=True,
                    plan_type=None
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                print("Default admin created from environment configuration")
        else:
            print("Admin bootstrap skipped. Set ADMIN_EMAIL and ADMIN_PASSWORD in .env to create one.")
    
    print("\n" + "="*60)
    print("🔐 ADMIN PORTAL - EnergyTrack")
    print("="*60)
    print("\n🌐 Admin Portal URL:")
    print("   Local:    http://127.0.0.1:5001")
    print("   Network:  http://[YOUR_IP]:5001")
    print("\n⚠️  IMPORTANT:")
    print("   - This admin portal runs on PORT 5001")
    print("   - User application runs on PORT 5000")
    print("   - Only admin accounts can access this portal")
    print("   - Configure firewall to restrict access")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=app.config.get('FLASK_DEBUG', False))
