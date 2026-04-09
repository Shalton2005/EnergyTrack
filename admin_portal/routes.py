"""
Admin portal module for system management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from models.database import db, User, SupportTicket, Payment, ConsumptionLog
from functools import wraps
from datetime import datetime, timedelta
from utils.timezone_utils import get_ist_now
from sqlalchemy import func

admin_bp = Blueprint('admin_portal', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('admin_portal.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page (separate from user login)"""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_portal.dashboard'))
    
    if request.method == 'POST':
        from flask_login import login_user
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, is_admin=True).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Admin login successful', 'success')
            return redirect(url_for('admin_portal.dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    
    return render_template('admin/login.html')


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with analytics"""
    # User statistics
    total_users = User.query.count()
    free_users = User.query.filter_by(plan_type='FREE').count()
    premium_users = User.query.filter(User.plan_type.in_(['PREMIUM_MONTHLY', 'PREMIUM_YEARLY'])).count()
    trial_users = User.query.filter(User.trial_ends_at > get_ist_now()).count()
    
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


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management"""
    all_users = User.query.order_by(User.created_at.desc()).all()
    open_tickets_count = SupportTicket.query.filter_by(status='open').count()
    return render_template('admin/users.html', users=all_users, open_tickets_count=open_tickets_count)


@admin_bp.route('/user/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View user details"""
    user = User.query.get_or_404(user_id)
    payments = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
    tickets = SupportTicket.query.filter_by(user_id=user_id).order_by(SupportTicket.created_at.desc()).all()
    open_tickets_count = SupportTicket.query.filter_by(status='open').count()
    
    return render_template('admin/user_detail.html', user=user, payments=payments, tickets=tickets, open_tickets_count=open_tickets_count)


@admin_bp.route('/tickets')
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


@admin_bp.route('/ticket/<int:ticket_id>/reply', methods=['POST'])
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
        
        # TODO: Send email to user with admin reply
        flash('Reply sent successfully', 'success')
    
    return redirect(url_for('admin_portal.tickets'))


@admin_bp.route('/revenue')
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


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """Admin settings (email configuration, etc.)"""
    from flask import current_app
    
    if request.method == 'POST':
        # Update admin email settings
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin_portal.settings'))
    
    # Get open tickets count for sidebar
    open_tickets_count = SupportTicket.query.filter_by(status='open').count()
    
    return render_template('admin/settings.html', 
                         config=current_app.config,
                         open_tickets_count=open_tickets_count)
