"""
IoT Device Control module for remote device management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.database import db, Device
from datetime import datetime
from utils.timezone_utils import get_ist_now
from functools import wraps

devices_bp = Blueprint('devices', __name__, url_prefix='/devices')


def premium_required(f):
    """Decorator to require premium subscription"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.has_premium():
            flash('This feature requires a Premium subscription. Please upgrade your plan.', 'warning')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@devices_bp.route('/')
@login_required
@premium_required
def index():
    """View all user devices"""
    user_devices = Device.query.filter_by(user_id=current_user.id).all()
    return render_template('devices/index.html', devices=user_devices)


@devices_bp.route('/add', methods=['GET', 'POST'])
@login_required
@premium_required
def add_device():
    """Add a new IoT device"""
    if request.method == 'POST':
        device_name = request.form.get('device_name')
        device_type = request.form.get('device_type')
        power_rating = request.form.get('power_rating', 0, type=float)
        room = request.form.get('room')
        
        if not all([device_name, device_type]):
            flash('Device name and type are required', 'danger')
            return render_template('devices/add.html')
        
        device = Device(
            user_id=current_user.id,
            device_name=device_name,
            device_type=device_type,
            power_rating=power_rating,
            room=room,
            is_online=True,
            is_on=False
        )
        
        db.session.add(device)
        db.session.commit()
        
        flash(f'Device "{device_name}" added successfully!', 'success')
        return redirect(url_for('devices.index'))
    
    return render_template('devices/add.html')


@devices_bp.route('/toggle/<int:device_id>', methods=['POST'])
@login_required
@premium_required
def toggle_device(device_id):
    """Toggle device ON/OFF"""
    device = Device.query.get_or_404(device_id)
    
    # Check ownership
    if device.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Toggle state (dummy implementation)
    device.is_on = not device.is_on
    device.last_toggled_at = get_ist_now()
    db.session.commit()
    
    # In real implementation, this would send command to IoT device via MQTT/WebSocket
    print(f"[IoT] Device {device.device_name} turned {'ON' if device.is_on else 'OFF'}")
    
    return jsonify({
        'success': True,
        'device_id': device.id,
        'device_name': device.device_name,
        'is_on': device.is_on,
        'message': f'{device.device_name} turned {"ON" if device.is_on else "OFF"}'
    })


@devices_bp.route('/delete/<int:device_id>', methods=['POST'])
@login_required
@premium_required
def delete_device(device_id):
    """Delete a device"""
    device = Device.query.get_or_404(device_id)
    
    if device.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('devices.index'))
    
    device_name = device.device_name
    db.session.delete(device)
    db.session.commit()
    
    flash(f'Device "{device_name}" deleted successfully', 'success')
    return redirect(url_for('devices.index'))


@devices_bp.route('/api/status')
@login_required
@premium_required
def device_status():
    """Get status of all devices (API endpoint)"""
    user_devices = Device.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'devices': [device.to_dict() for device in user_devices]
    })
