"""
Authentication module for user registration, login, and password management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from models.database import db, User, OTPRecord
from datetime import datetime, timedelta
from utils.timezone_utils import get_ist_now
import random
import string

auth_bp = Blueprint('auth', __name__)

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def send_welcome_email(user):
    """Send welcome email (optional, won't crash if not configured)"""
    try:
        # Only try to send if mail is configured
        if not current_app.config.get('MAIL_USERNAME'):
            print(f"[INFO] Email not configured. Skipping welcome email for {user.email}")
            return False
        
        # Import mail from app
        from app import mail
        
        subject = "Welcome to EnergyTrack!"
        sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
        
        body = f"""
Hello {user.name},

Welcome to EnergyTrack - Smart Energy Monitoring System!

Your account has been created successfully.
You can now login and start monitoring your energy consumption.

Email: {user.email}
Plan: {user.plan_type}

Best regards,
EnergyTrack Team
        """
        
        msg = Message(subject=subject, sender=sender, recipients=[user.email], body=body)
        mail.send(msg)
        print(f"[SUCCESS] Welcome email sent to {user.email} from {sender}")
        return True
    except Exception as e:
        print(f"[WARNING] Email notification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def send_otp_email(user, otp_code, purpose):
    """Send OTP via email"""
    try:
        if not current_app.config.get('MAIL_USERNAME'):
            print(f"[INFO] Email not configured. OTP for {user.email}: {otp_code}")
            return False
        
        # Import mail from app
        from app import mail
        sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
        
        subject = "EnergyTrack - Email Verification" if purpose == 'verification' else "EnergyTrack - Password Reset"
        body = f"""
        Hello {user.name},
        
        Your OTP code is: {otp_code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        EnergyTrack Team
        """
        
        msg = Message(subject=subject, sender=sender, recipients=[user.email], body=body)
        mail.send(msg)
        print(f"[SUCCESS] OTP email sent to {user.email} from {sender}")
        return True
    except Exception as e:
        print(f"[WARNING] Email error (OTP printed to console): {e}")
        print(f"OTP for {user.email}: {otp_code}")
        return False


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        electricity_provider = request.form.get('electricity_provider')
        rr_number = request.form.get('rr_number')
        plan_type = request.form.get('plan_type', 'FREE')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, phone, electricity_provider, rr_number, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('auth/register.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')
        
        # Create user (auto-verified, no OTP required)
        user = User(
            name=name, 
            email=email, 
            phone_number=phone,
            electricity_provider=electricity_provider,
            rr_number=rr_number,
            plan_type=plan_type,
            is_verified=True
        )
        user.set_password(password)
        
        # Set trial period for premium users
        if plan_type in ['PREMIUM_MONTHLY', 'PREMIUM_YEARLY']:
            from datetime import timedelta
            user.trial_ends_at = get_ist_now() + timedelta(days=30)  # 1 month trial
            user.subscription_started_at = get_ist_now()
        
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email (optional, doesn't block registration)
        try:
            send_welcome_email(user)
        except:
            pass  # Email is optional
        
        if plan_type in ['PREMIUM_MONTHLY', 'PREMIUM_YEARLY']:
            flash('Registration successful! You have 1 month free trial. Please login', 'success')
        else:
            flash('Registration successful! Please login', 'success')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Email OTP verification"""
    user_id = session.get('verification_user_id')
    if not user_id:
        return redirect(url_for('auth.register'))
    
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp')
        
        # Find valid OTP
        otp_record = OTPRecord.query.filter_by(
            user_id=user.id,
            otp_code=otp_code,
            purpose='verification',
            is_used=False
        ).first()
        
        if not otp_record:
            flash('Invalid OTP code', 'danger')
            return render_template('auth/verify_email.html')
        
        if get_ist_now() > otp_record.expires_at:
            flash('OTP expired. Please request a new one', 'danger')
            return render_template('auth/verify_email.html')
        
        # Mark as verified
        user.is_verified = True
        otp_record.is_used = True
        db.session.commit()
        
        session.pop('verification_user_id', None)
        flash('Email verified successfully! Please login', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/verify_email.html', email=user.email)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html')
        
        # Block admin users from logging into user app
        if user.is_admin:
            flash('Admin accounts cannot login here. Please use the Admin Portal at http://127.0.0.1:5001', 'danger')
            return render_template('auth/login.html')
        
        # Auto-verify if not verified (backward compatibility)
        if not user.is_verified:
            user.is_verified = True
            db.session.commit()
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        
        return redirect(next_page or url_for('dashboard.index'))
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password - send OTP"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email not found', 'danger')
            return render_template('auth/forgot_password.html')
        
        # Generate OTP
        otp_code = generate_otp()
        otp_record = OTPRecord(
            user_id=user.id,
            otp_code=otp_code,
            purpose='reset_password',
            expires_at=get_ist_now() + timedelta(minutes=10)
        )
        db.session.add(otp_record)
        db.session.commit()
        
        # Always allow password reset, print OTP to console if email fails
        print(f"\n{'='*60}")
        print(f"PASSWORD RESET OTP for {user.email}: {otp_code}")
        print(f"{'='*60}\n")
        
        send_otp_email(user, otp_code, 'reset_password')  # Try to send, but don't block
        
        session['reset_user_id'] = user.id
        flash('OTP generated! Check console if email not configured', 'info')
        return redirect(url_for('auth.reset_password'))
    
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password with OTP"""
    user_id = session.get('reset_user_id')
    if not user_id:
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/reset_password.html', email=user.email)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('auth/reset_password.html', email=user.email)
        
        # Verify OTP
        otp_record = OTPRecord.query.filter_by(
            user_id=user.id,
            otp_code=otp_code,
            purpose='reset_password',
            is_used=False
        ).first()
        
        if not otp_record:
            flash('Invalid OTP code', 'danger')
            return render_template('auth/reset_password.html', email=user.email)
        
        if get_ist_now() > otp_record.expires_at:
            flash('OTP expired. Please request a new one', 'danger')
            return redirect(url_for('auth.forgot_password'))
        
        # Update password
        user.set_password(new_password)
        otp_record.is_used = True
        db.session.commit()
        
        session.pop('reset_user_id', None)
        flash('Password reset successful! Please login', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', email=user.email)
