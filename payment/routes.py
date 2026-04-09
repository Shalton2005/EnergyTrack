"""
Payment Gateway module for subscription management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.database import db, Payment, User
from datetime import datetime, timedelta
from utils.timezone_utils import get_ist_now
import random
import string

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')


def generate_transaction_id():
    """Generate unique transaction ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'TXN{timestamp}{random_str}'


@payment_bp.route('/upgrade')
@login_required
def upgrade():
    """Show upgrade options"""
    return render_template('payment/upgrade.html')


@payment_bp.route('/checkout/<plan_type>')
@login_required
def checkout(plan_type):
    """Checkout page for payment"""
    if plan_type not in ['PREMIUM_MONTHLY', 'PREMIUM_YEARLY']:
        flash('Invalid plan selected', 'danger')
        return redirect(url_for('payment.upgrade'))
    
    # Calculate amount
    amount = 99 if plan_type == 'PREMIUM_MONTHLY' else 999
    
    return render_template('payment/checkout.html', 
                         plan_type=plan_type, 
                         amount=amount)


@payment_bp.route('/process', methods=['POST'])
@login_required
def process_payment():
    """Process payment (dummy implementation)"""
    plan_type = request.form.get('plan_type')
    amount = float(request.form.get('amount'))
    payment_method = request.form.get('payment_method', 'razorpay')
    
    # Simulate payment processing
    simulate_failure = request.form.get('simulate_failure') == 'true'
    
    # Generate transaction ID
    transaction_id = generate_transaction_id()
    
    # Create payment record
    payment = Payment(
        user_id=current_user.id,
        amount=amount,
        plan_type=plan_type,
        payment_method=payment_method,
        transaction_id=transaction_id,
        status='pending'
    )
    
    db.session.add(payment)
    db.session.commit()
    
    # Simulate payment processing delay
    import time
    time.sleep(1)
    
    if simulate_failure:
        # Simulate payment failure
        payment.status = 'failed'
        db.session.commit()
        
        flash('Payment failed! Please try again.', 'danger')
        return redirect(url_for('payment.failure', transaction_id=transaction_id))
    else:
        # Simulate payment success
        payment.status = 'SUCCESS'
        db.session.commit()
        
        # Update user subscription
        current_user.plan_type = plan_type
        current_user.subscription_started_at = get_ist_now()
        
        # Remove trial (if any) and set subscription date
        if plan_type == 'PREMIUM_MONTHLY':
            # Monthly subscription - set trial end to 1 month from now
            current_user.trial_ends_at = None
        elif plan_type == 'PREMIUM_YEARLY':
            # Yearly subscription
            current_user.trial_ends_at = None
        
        db.session.commit()
        
        flash('Payment successful! Your subscription is now active.', 'success')
        return redirect(url_for('payment.success', transaction_id=transaction_id))


@payment_bp.route('/success/<transaction_id>')
@login_required
def success(transaction_id):
    """Payment success page"""
    payment = Payment.query.filter_by(transaction_id=transaction_id).first_or_404()
    
    # Check if this payment belongs to current user
    if payment.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('payment/success.html', payment=payment)


@payment_bp.route('/failure/<transaction_id>')
@login_required
def failure(transaction_id):
    """Payment failure page"""
    payment = Payment.query.filter_by(transaction_id=transaction_id).first_or_404()
    
    # Check if this payment belongs to current user
    if payment.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('payment/failure.html', payment=payment)


@payment_bp.route('/history')
@login_required
def history():
    """Payment history page"""
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).all()
    return render_template('payment/history.html', payments=payments)


@payment_bp.route('/cancel-subscription', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel current subscription"""
    if current_user.plan_type == 'FREE':
        flash('You are already on the FREE plan', 'info')
        return redirect(url_for('dashboard.index'))
    
    # Downgrade to FREE
    current_user.plan_type = 'FREE'
    current_user.trial_ends_at = None
    current_user.subscription_started_at = None
    db.session.commit()
    
    flash('Your subscription has been cancelled. You are now on the FREE plan.', 'info')
    return redirect(url_for('dashboard.index'))
