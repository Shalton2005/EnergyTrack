"""
Admin panel routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.database import db, User, ConsumptionLog, Alert
from functools import wraps
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    # Get statistics
    total_users = User.query.count()
    verified_users = User.query.filter_by(is_verified=True).count()
    total_logs = ConsumptionLog.query.count()
    total_alerts = Alert.query.count()
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    return render_template('admin/index.html',
                         total_users=total_users,
                         verified_users=verified_users,
                         total_logs=total_logs,
                         total_alerts=total_alerts,
                         recent_users=recent_users)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """List all users"""
    all_users = User.query.order_by(User.created_at.desc()).all()
    
    # Calculate consumption for each user
    user_stats = []
    for user in all_users:
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        logs = ConsumptionLog.query.filter(
            ConsumptionLog.user_id == user.id,
            ConsumptionLog.timestamp >= month_start
        ).all()
        
        monthly_kwh = sum([log.global_active_power for log in logs]) / 60 if logs else 0
        
        user_stats.append({
            'user': user,
            'monthly_consumption': round(monthly_kwh, 2),
            'total_logs': ConsumptionLog.query.filter_by(user_id=user.id).count()
        })
    
    return render_template('admin/users.html', user_stats=user_stats)


@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user account"""
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        return jsonify({'error': 'Cannot delete admin account'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.email} deleted successfully', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/logs/<int:user_id>')
@login_required
@admin_required
def user_logs(user_id):
    """View user consumption logs"""
    user = User.query.get_or_404(user_id)
    
    # Get recent logs
    logs = ConsumptionLog.query.filter_by(user_id=user_id).order_by(
        ConsumptionLog.timestamp.desc()
    ).limit(100).all()
    
    return render_template('admin/user_logs.html', user=user, logs=logs)


@admin_bp.route('/api/system-stats')
@login_required
@admin_required
def system_stats():
    """API endpoint for system statistics"""
    # Daily new users (last 7 days)
    daily_users = []
    for i in range(6, -1, -1):
        day = datetime.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        count = User.query.filter(
            User.created_at >= day_start,
            User.created_at < day_end
        ).count()
        
        daily_users.append({
            'date': day.strftime('%a'),
            'count': count
        })
    
    # Total consumption trend
    daily_consumption = []
    for i in range(6, -1, -1):
        day = datetime.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        logs = ConsumptionLog.query.filter(
            ConsumptionLog.timestamp >= day_start,
            ConsumptionLog.timestamp < day_end
        ).all()
        
        total_kwh = sum([log.global_active_power for log in logs]) / 60 if logs else 0
        
        daily_consumption.append({
            'date': day.strftime('%a'),
            'consumption': round(total_kwh, 2)
        })
    
    return jsonify({
        'daily_users': daily_users,
        'daily_consumption': daily_consumption
    })
