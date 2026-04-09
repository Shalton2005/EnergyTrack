"""
Dashboard routes for main application features
"""
from flask import Blueprint, render_template, jsonify, request, session, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from models.database import db, ConsumptionLog, Alert, DeviceLog, User
from ml.predictor import EnergyPredictor
from ml.device_identifier import DeviceIdentifier
from ml.appliance_detector import ApplianceDetector
from utils.bill_generator import generate_bill_pdf, calculate_bill
from datetime import datetime, timedelta
import pandas as pd
import random

dashboard_bp = Blueprint('dashboard', __name__)

# Global variables for simulation
simulation_index = 0
dataset_df = None


def load_dataset():
    """Load dataset for simulation"""
    global dataset_df
    try:
        dataset_df = pd.read_csv('dataset.csv')
        dataset_df['datetime'] = pd.to_datetime(dataset_df['datetime'])
        return True
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return False


def get_next_data_point():
    """Get next data point from dataset for simulation"""
    global simulation_index, dataset_df
    
    if dataset_df is None:
        if not load_dataset():
            # Return dummy data if dataset not found
            return {
                'datetime': datetime.now().isoformat(),
                'global_active_power': round(random.uniform(0.5, 3.0), 3),
                'voltage': round(random.uniform(220, 240), 1),
                'current': round(random.uniform(2, 12), 2),
                'sub_metering1': round(random.uniform(0, 30), 1),
                'sub_metering2': round(random.uniform(0, 25), 1),
                'sub_metering3': round(random.uniform(0, 20), 1)
            }
    
    if simulation_index >= len(dataset_df):
        simulation_index = 0
    
    row = dataset_df.iloc[simulation_index]
    simulation_index += 1
    
    return {
        'datetime': row['datetime'].isoformat() if pd.notna(row['datetime']) else datetime.now().isoformat(),
        'global_active_power': float(row['global_active_power']) if pd.notna(row['global_active_power']) else 0.0,
        'voltage': float(row['voltage']) if pd.notna(row['voltage']) else 230.0,
        'current': float(row['current']) if pd.notna(row['current']) else 0.0,
        'sub_metering1': float(row['sub_metering1']) if pd.notna(row['sub_metering1']) else 0.0,
        'sub_metering2': float(row['sub_metering2']) if pd.notna(row['sub_metering2']) else 0.0,
        'sub_metering3': float(row['sub_metering3']) if pd.notna(row['sub_metering3']) else 0.0
    }


def check_alerts(data, user_id):
    """Check for alert conditions and create alerts"""
    from config import Config
    
    alerts_created = []
    
    # Voltage fluctuation alert
    if current_user.voltage_alerts:
        if data['voltage'] < Config.VOLTAGE_MIN or data['voltage'] > Config.VOLTAGE_MAX:
            alert = Alert(
                user_id=user_id,
                alert_type='voltage',
                message=f"Voltage fluctuation detected: {data['voltage']}V (Normal: {Config.VOLTAGE_MIN}-{Config.VOLTAGE_MAX}V)",
                severity='warning'
            )
            db.session.add(alert)
            alerts_created.append(alert)
    
    # Power spike alert
    recent_logs = ConsumptionLog.query.filter_by(user_id=user_id).order_by(
        ConsumptionLog.timestamp.desc()
    ).limit(5).all()
    
    if len(recent_logs) > 0:
        avg_power = sum([log.global_active_power for log in recent_logs]) / len(recent_logs)
        if data['global_active_power'] > avg_power * 2 and data['global_active_power'] > 2.0:
            alert = Alert(
                user_id=user_id,
                alert_type='spike',
                message=f"Sudden power spike detected: {data['global_active_power']:.2f} kW",
                severity='danger'
            )
            db.session.add(alert)
            alerts_created.append(alert)
    
    if alerts_created:
        db.session.commit()
    
    return alerts_created


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page"""
    # Get user stats
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    today_logs = ConsumptionLog.query.filter(
        ConsumptionLog.user_id == current_user.id,
        ConsumptionLog.timestamp >= today
    ).all()
    
    today_consumption = sum([log.global_active_power for log in today_logs]) / 60 if today_logs else 0
    
    # Get recent alerts
    recent_alerts = Alert.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Alert.created_at.desc()).limit(5).all()
    
    return render_template('dashboard/index.html',
                         today_consumption=round(today_consumption, 2),
                         alert_count=len(recent_alerts))


@dashboard_bp.route('/api/live-data')
@login_required
def live_data():
    """API endpoint for live data streaming"""
    # Get next data point
    data = get_next_data_point()
    
    # Save to database
    log = ConsumptionLog(
        user_id=current_user.id,
        timestamp=datetime.now(),
        global_active_power=data['global_active_power'],
        voltage=data['voltage'],
        current=data['current'],
        sub_metering1=data['sub_metering1'],
        sub_metering2=data['sub_metering2'],
        sub_metering3=data['sub_metering3']
    )
    db.session.add(log)
    db.session.commit()
    
    # Check for alerts
    check_alerts(data, current_user.id)
    
    # Calculate today's consumption (kWh = sum of kW readings / 60)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_logs = ConsumptionLog.query.filter(
        ConsumptionLog.user_id == current_user.id,
        ConsumptionLog.timestamp >= today
    ).all()
    today_consumption = sum([log.global_active_power for log in today_logs]) / 60 if today_logs else 0
    
    # Calculate monthly estimate (based on average daily usage)
    days_in_month = 30
    if datetime.now().day > 0 and datetime.now().hour > 0:
        daily_avg = (today_consumption / (datetime.now().hour + 1)) * 24
        monthly_estimate = daily_avg * days_in_month
    else:
        monthly_estimate = 0
    
    # Get recent unread alerts
    recent_alerts = Alert.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Alert.created_at.desc()).limit(5).all()
    
    # Get predictions
    predictor = EnergyPredictor()
    next_prediction = predictor.predict_next_consumption(data)
    
    # AI Appliance Detection
    detector = ApplianceDetector()
    # Get last 10 readings for pattern analysis
    recent_logs = ConsumptionLog.query.filter_by(user_id=current_user.id).order_by(
        ConsumptionLog.timestamp.desc()
    ).limit(10).all()
    
    detected_appliances = []
    if len(recent_logs) >= 5:
        # Prepare data for detection
        power_readings = [log.global_active_power * 1000 for log in reversed(recent_logs)]  # Convert to watts
        voltage_readings = [log.voltage for log in reversed(recent_logs)]
        
        # Detect appliances
        detections = detector.detect_appliances(power_readings, voltage_readings)
        detected_appliances = [{
            'name': d['appliance'],
            'confidence': round(d['confidence'], 1),
            'power': round(d['estimated_power'], 0),
            'cost_per_hour': round(d['cost_per_hour'], 2)
        } for d in detections[:3]]  # Top 3 detections
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'current_power': round(data['global_active_power'], 3),
        'voltage': round(data['voltage'], 1),
        'current': round(data['current'], 2),
        'sub_metering1': round(data['sub_metering1'], 1),
        'sub_metering2': round(data['sub_metering2'], 1),
        'sub_metering3': round(data['sub_metering3'], 1),
        'today_consumption': round(today_consumption, 2),
        'monthly_estimate': round(monthly_estimate, 2),
        'next_prediction': round(next_prediction, 3) if next_prediction else None,
        'alert_count': len(recent_alerts),
        'alerts': [{
            'id': alert.id,
            'message': alert.message,
            'severity': alert.severity,
            'created_at': alert.created_at.strftime('%I:%M %p')
        } for alert in recent_alerts],
        'detected_appliances': detected_appliances
    })


@dashboard_bp.route('/api/chart-data/<chart_type>')
@login_required
def chart_data(chart_type):
    """Get data for charts"""
    if chart_type == 'live':
        # Last 20 data points
        logs = ConsumptionLog.query.filter_by(user_id=current_user.id).order_by(
            ConsumptionLog.timestamp.desc()
        ).limit(20).all()
        logs.reverse()
        
        return jsonify({
            'labels': [log.timestamp.strftime('%H:%M:%S') for log in logs],
            'power': [round(log.global_active_power, 2) for log in logs],
            'voltage': [round(log.voltage, 1) for log in logs]
        })
    
    elif chart_type == 'daily':
        # Last 7 days consumption
        days_data = []
        for i in range(6, -1, -1):
            day = datetime.now() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            logs = ConsumptionLog.query.filter(
                ConsumptionLog.user_id == current_user.id,
                ConsumptionLog.timestamp >= day_start,
                ConsumptionLog.timestamp < day_end
            ).all()
            
            daily_kwh = sum([log.global_active_power for log in logs]) / 60 if logs else 0
            days_data.append({
                'date': day.strftime('%a'),
                'consumption': round(daily_kwh, 2)
            })
        
        return jsonify({
            'labels': [d['date'] for d in days_data],
            'consumption': [d['consumption'] for d in days_data]
        })
    
    return jsonify({'error': 'Invalid chart type'}), 400


@dashboard_bp.route('/billing')
@login_required
def billing():
    """Billing page"""
    # Calculate current month consumption
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    logs = ConsumptionLog.query.filter(
        ConsumptionLog.user_id == current_user.id,
        ConsumptionLog.timestamp >= month_start
    ).all()
    
    monthly_kwh = sum([log.global_active_power for log in logs]) / 60 if logs else 0
    
    # Get tariff and calculate bill
    tariff = current_user.get_tariff()
    predictor = EnergyPredictor()
    bill_details = predictor.calculate_bill(monthly_kwh, tariff)
    
    return render_template('dashboard/billing.html',
                         monthly_kwh=round(monthly_kwh, 2),
                         bill_details=bill_details,
                         tariff=tariff,
                         current_date=datetime.now())


@dashboard_bp.route('/alerts')
@login_required
def alerts():
    """Alerts page"""
    all_alerts = Alert.query.filter_by(user_id=current_user.id).order_by(
        Alert.created_at.desc()
    ).all()
    
    return render_template('dashboard/alerts.html', alerts=all_alerts)


@dashboard_bp.route('/api/mark-alert-read/<int:alert_id>', methods=['POST'])
@login_required
def mark_alert_read(alert_id):
    """Mark alert as read"""
    alert = Alert.query.get_or_404(alert_id)
    
    if alert.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    alert.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})


@dashboard_bp.route('/devices')
@login_required
def devices():
    """Device identification page"""
    # Get recent consumption data
    recent_log = ConsumptionLog.query.filter_by(user_id=current_user.id).order_by(
        ConsumptionLog.timestamp.desc()
    ).first()
    
    identified_devices = []
    if recent_log:
        identifier = DeviceIdentifier()
        data = {
            'global_active_power': recent_log.global_active_power,
            'sub_metering1': recent_log.sub_metering1,
            'sub_metering2': recent_log.sub_metering2,
            'sub_metering3': recent_log.sub_metering3
        }
        identified_devices = identifier.identify_devices(data)
    
    return render_template('dashboard/devices.html', devices=identified_devices)


@dashboard_bp.route('/support')
@login_required
def support():
    """Support tickets page for users"""
    # For now, return a simple support page
    # In the future, add SupportTicket model and database functionality
    return render_template('dashboard/support.html')


@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page with update functionality"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            # Update basic profile info
            current_user.name = request.form.get('name')
            current_user.phone_number = request.form.get('phone_number')
            current_user.electricity_provider = request.form.get('electricity_provider')
            current_user.rr_number = request.form.get('rr_number')
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            
        elif action == 'update_email':
            new_email = request.form.get('new_email')
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user and existing_user.id != current_user.id:
                flash('Email already in use by another account', 'danger')
            else:
                current_user.email = new_email
                db.session.commit()
                flash('Email updated successfully!', 'success')
                
        elif action == 'update_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'danger')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters long', 'danger')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password updated successfully!', 'success')
                
        elif action == 'delete_account':
            password = request.form.get('confirm_password')
            
            if not current_user.check_password(password):
                flash('Incorrect password. Account deletion cancelled.', 'danger')
            else:
                # Delete all user data
                user_id = current_user.id
                user_name = current_user.name
                
                # Delete related data
                from models.database import Payment, SupportTicket, ConsumptionLog, Alert, DeviceLog
                Payment.query.filter_by(user_id=user_id).delete()
                SupportTicket.query.filter_by(user_id=user_id).delete()
                ConsumptionLog.query.filter_by(user_id=user_id).delete()
                Alert.query.filter_by(user_id=user_id).delete()
                DeviceLog.query.filter_by(user_id=user_id).delete()
                
                # Delete user
                db.session.delete(current_user)
                db.session.commit()
                
                # Logout
                from flask_login import logout_user
                logout_user()
                
                flash(f'Account for {user_name} has been permanently deleted.', 'info')
                return redirect(url_for('auth.register'))
        
        return redirect(url_for('dashboard.profile'))
    
    return render_template('dashboard/profile.html')


@dashboard_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not current_user.check_password(current_password):
                return jsonify({'error': 'Current password is incorrect'}), 400
            
            if new_password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400
            
            current_user.set_password(new_password)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Password updated successfully'})
        
        elif action == 'update_tariff':
            import json
            tariff_json = request.form.get('tariff_json')
            
            try:
                tariff = json.loads(tariff_json)
                current_user.set_tariff(tariff)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Tariff updated successfully'})
            except:
                return jsonify({'error': 'Invalid tariff format'}), 400
        
        elif action == 'update_alerts':
            current_user.voltage_alerts = request.form.get('voltage_alerts') == 'on'
            current_user.bill_alerts = request.form.get('bill_alerts') == 'on'
            current_user.email_notifications = request.form.get('email_notifications') == 'on'
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Alert preferences updated'})
    
    return render_template('dashboard/settings.html', tariff=current_user.get_tariff())


@dashboard_bp.route('/generate-bill')
@login_required
def generate_bill():
    """Generate electricity bill PDF"""
    # Get monthly consumption
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    logs = ConsumptionLog.query.filter(
        ConsumptionLog.user_id == current_user.id,
        ConsumptionLog.timestamp >= month_start
    ).all()
    
    # Calculate total kWh
    total_kwh = sum([log.global_active_power for log in logs]) / 60 if logs else 0
    
    # Generate billing period string
    billing_period = month_start.strftime('%B %Y')
    
    # Generate PDF
    pdf_buffer = generate_bill_pdf(current_user, billing_period, total_kwh)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f'electricity_bill_{month_start.strftime("%Y_%m")}.pdf',
        mimetype='application/pdf'
    )


@dashboard_bp.route('/bill-preview')
@login_required
def bill_preview():
    """Preview bill calculation"""
    from utils.timezone_utils import get_ist_now
    
    # Get monthly consumption
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    logs = ConsumptionLog.query.filter(
        ConsumptionLog.user_id == current_user.id,
        ConsumptionLog.timestamp >= month_start
    ).all()
    
    # Calculate total kWh
    total_kwh = sum([log.global_active_power for log in logs]) / 60 if logs else 0
    
    # Calculate bill
    provider = current_user.electricity_provider or 'OTHER'
    bill = calculate_bill(total_kwh, provider)
    
    # Add consumer and billing details
    now = get_ist_now()
    bill['consumer_name'] = current_user.name
    bill['consumer_email'] = current_user.email
    bill['consumer_phone'] = current_user.phone_number or 'N/A'
    bill['rr_number'] = current_user.rr_number or 'Not Set'
    bill['billing_period'] = month_start.strftime('%B %Y')
    bill['bill_date'] = now.strftime('%d %b %Y')
    bill['due_date'] = (now + timedelta(days=15)).strftime('%d %b %Y')
    
    return render_template('dashboard/bill_preview.html', bill=bill)
