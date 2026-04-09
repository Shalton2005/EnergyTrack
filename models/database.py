"""
Database models for EnergyTrack application
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from utils.timezone_utils import get_ist_now
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and profile"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Electricity Provider Info
    electricity_provider = db.Column(db.String(100), nullable=True)  # MESCOM, BESCOM, etc.
    rr_number = db.Column(db.String(50), nullable=True)  # RR/MR Number
    
    # Subscription
    plan_type = db.Column(db.String(20), default='FREE')  # FREE, PREMIUM_MONTHLY, PREMIUM_YEARLY
    trial_ends_at = db.Column(db.DateTime, nullable=True)
    subscription_started_at = db.Column(db.DateTime, nullable=True)
    
    tariff_json = db.Column(db.Text, nullable=True)  # JSON string of tariff slabs
    created_at = db.Column(db.DateTime, default=get_ist_now)
    
    # Settings
    voltage_alerts = db.Column(db.Boolean, default=True)
    bill_alerts = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)
    
    # Relationships
    consumption_logs = db.relationship('ConsumptionLog', backref='user', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='user', lazy=True, cascade='all, delete-orphan')
    otp_records = db.relationship('OTPRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    devices = db.relationship('Device', backref='user', lazy=True, cascade='all, delete-orphan')
    support_tickets = db.relationship('SupportTicket', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def has_premium(self):
        """Check if user has premium subscription"""
        if self.plan_type in ['PREMIUM_MONTHLY', 'PREMIUM_YEARLY']:
            return True
        # Check if trial is still active
        if self.trial_ends_at and self.trial_ends_at > get_ist_now():
            return True
        return False
    
    def is_premium_active(self):
        """Check if premium subscription is active (excluding trial)"""
        return self.plan_type in ['PREMIUM_MONTHLY', 'PREMIUM_YEARLY']
    
    def trial_days_remaining(self):
        """Get remaining trial days"""
        if self.trial_ends_at:
            try:
                now = get_ist_now()
                # Ensure both datetimes are timezone-aware for comparison
                trial_end = self.trial_ends_at
                if trial_end.tzinfo is None:
                    from utils.timezone_utils import IST
                    trial_end = IST.localize(trial_end)
                
                if trial_end > now:
                    delta = trial_end - now
                    return delta.days
            except (TypeError, AttributeError):
                return 0
        return 0
    
    def get_tariff(self):
        """Get tariff as dictionary"""
        if self.tariff_json:
            return json.loads(self.tariff_json)
        # Default Karnataka MESCOM tariff
        return {
            "fixed_charges": 100,
            "slabs": [
                {"up_to": 50, "rate": 3.40},
                {"up_to": 100, "rate": 4.95},
                {"up_to": 200, "rate": 6.50},
                {"above": 200, "rate": 7.55}
            ]
        }
    
    def set_tariff(self, tariff_dict):
        """Set tariff from dictionary"""
        self.tariff_json = json.dumps(tariff_dict)


class OTPRecord(db.Model):
    """OTP verification records"""
    __tablename__ = 'otp_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)  # 'verification' or 'reset_password'
    created_at = db.Column(db.DateTime, default=get_ist_now)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)


class ConsumptionLog(db.Model):
    """Energy consumption logs"""
    __tablename__ = 'consumption_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    global_active_power = db.Column(db.Float, nullable=False)  # kW
    voltage = db.Column(db.Float, nullable=False)  # V
    current = db.Column(db.Float, nullable=False)  # A
    sub_metering1 = db.Column(db.Float, default=0)  # Wh
    sub_metering2 = db.Column(db.Float, default=0)  # Wh
    sub_metering3 = db.Column(db.Float, default=0)  # Wh
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'global_active_power': self.global_active_power,
            'voltage': self.voltage,
            'current': self.current,
            'sub_metering1': self.sub_metering1,
            'sub_metering2': self.sub_metering2,
            'sub_metering3': self.sub_metering3
        }


class Alert(db.Model):
    """User alerts and notifications"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # 'voltage', 'spike', 'consumption', 'prediction'
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='info')  # 'info', 'warning', 'danger'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_ist_now)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'message': self.message,
            'severity': self.severity,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }


class DeviceLog(db.Model):
    """Identified device activity logs"""
    __tablename__ = 'device_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    estimated_power = db.Column(db.Float, nullable=False)  # kW
    duration = db.Column(db.Integer, nullable=False)  # minutes
    timestamp = db.Column(db.DateTime, default=get_ist_now)
    
    user = db.relationship('User', backref='device_logs')


class Device(db.Model):
    """IoT Devices for remote control"""
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)  # 'light', 'fan', 'ac', 'heater', 'other'
    power_rating = db.Column(db.Float, default=0)  # Watts
    is_online = db.Column(db.Boolean, default=True)
    is_on = db.Column(db.Boolean, default=False)
    room = db.Column(db.String(50), nullable=True)  # bedroom, living_room, kitchen, etc.
    created_at = db.Column(db.DateTime, default=get_ist_now)
    last_toggled_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'power_rating': self.power_rating,
            'is_online': self.is_online,
            'is_on': self.is_on,
            'room': self.room,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_toggled_at': self.last_toggled_at.isoformat() if self.last_toggled_at else None
        }


class SupportTicket(db.Model):
    """Support tickets from users"""
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for guest tickets
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')  # open, in_progress, closed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    admin_reply = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_ist_now)
    updated_at = db.Column(db.DateTime, default=get_ist_now, onupdate=get_ist_now)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'priority': self.priority,
            'admin_reply': self.admin_reply,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Payment(db.Model):
    """Payment transactions (dummy for now)"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    plan_type = db.Column(db.String(20), nullable=False)  # PREMIUM_MONTHLY, PREMIUM_YEARLY
    payment_method = db.Column(db.String(50), default='razorpay')
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, SUCCESS, failed
    created_at = db.Column(db.DateTime, default=get_ist_now)
    
    user = db.relationship('User', backref='payments')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'amount': self.amount,
            'plan_type': self.plan_type,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

