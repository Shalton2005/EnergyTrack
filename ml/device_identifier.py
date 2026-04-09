"""
Device identification module using NILM-like logic
"""


class DeviceIdentifier:
    """Identify appliances based on consumption patterns"""
    
    # Device signatures (simplified)
    DEVICE_PATTERNS = {
        'Refrigerator': {
            'min_power': 0.1,
            'max_power': 0.3,
            'pattern': 'cyclic',
            'sub_meter': 1
        },
        'Water Heater/Geyser': {
            'min_power': 1.5,
            'max_power': 3.0,
            'pattern': 'constant',
            'sub_meter': 2
        },
        'Air Conditioner': {
            'min_power': 1.0,
            'max_power': 2.5,
            'pattern': 'constant',
            'sub_meter': 1
        },
        'Iron Box': {
            'min_power': 0.8,
            'max_power': 1.5,
            'pattern': 'spike',
            'sub_meter': 3
        },
        'Electric Kettle': {
            'min_power': 1.2,
            'max_power': 2.0,
            'pattern': 'spike',
            'sub_meter': 2
        },
        'Washing Machine': {
            'min_power': 0.5,
            'max_power': 1.2,
            'pattern': 'cyclic',
            'sub_meter': 3
        },
        'Lights & Fans': {
            'min_power': 0.05,
            'max_power': 0.3,
            'pattern': 'constant',
            'sub_meter': 1
        },
        'TV & Electronics': {
            'min_power': 0.1,
            'max_power': 0.4,
            'pattern': 'constant',
            'sub_meter': 1
        }
    }
    
    def __init__(self):
        self.active_devices = []
    
    def identify_devices(self, consumption_data):
        """Identify active devices from consumption data"""
        identified = []
        
        power = consumption_data.get('global_active_power', 0)
        sub1 = consumption_data.get('sub_metering1', 0) / 1000  # Convert Wh to kWh
        sub2 = consumption_data.get('sub_metering2', 0) / 1000
        sub3 = consumption_data.get('sub_metering3', 0) / 1000
        
        # Check each device pattern
        for device_name, pattern in self.DEVICE_PATTERNS.items():
            min_p = pattern['min_power']
            max_p = pattern['max_power']
            sub_meter = pattern['sub_meter']
            
            # Get relevant sub-meter reading
            sub_power = sub1 if sub_meter == 1 else (sub2 if sub_meter == 2 else sub3)
            
            # Check if power matches device signature
            if min_p <= sub_power <= max_p:
                identified.append({
                    'device': device_name,
                    'estimated_power': round(sub_power, 2),
                    'confidence': 'medium'
                })
            elif min_p <= power <= max_p and sub_power > 0:
                identified.append({
                    'device': device_name,
                    'estimated_power': round(power, 2),
                    'confidence': 'low'
                })
        
        # Always-on baseline
        if power > 0.05 and len(identified) == 0:
            identified.append({
                'device': 'Standby Devices',
                'estimated_power': round(power, 2),
                'confidence': 'low'
            })
        
        return identified
    
    def detect_spikes(self, current_power, previous_power, threshold=0.5):
        """Detect sudden power spikes"""
        if previous_power and abs(current_power - previous_power) > threshold:
            return True
        return False
    
    def estimate_device_usage(self, device_logs):
        """Calculate device-wise energy consumption"""
        device_summary = {}
        
        for log in device_logs:
            device = log['device']
            power = log['estimated_power']
            duration = log.get('duration', 60)  # minutes
            
            # Calculate energy (kWh)
            energy = (power * duration) / 60
            
            if device in device_summary:
                device_summary[device]['total_energy'] += energy
                device_summary[device]['count'] += 1
            else:
                device_summary[device] = {
                    'total_energy': energy,
                    'count': 1,
                    'avg_power': power
                }
        
        return device_summary
