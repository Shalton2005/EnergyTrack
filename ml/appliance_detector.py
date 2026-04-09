"""
AI-Powered Appliance Detection Module
Uses Non-Intrusive Load Monitoring (NILM) to identify appliances
from power consumption signatures
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os


class ApplianceDetector:
    """
    Detects which appliances are running based on power consumption patterns
    This is a UNIQUE feature that sets EnergyTrack apart from competitors
    """
    
    def __init__(self, model_path='ml/appliance_model.pkl'):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path
        
        # Appliance power signatures (typical Indian households)
        self.appliance_profiles = {
            'Air Conditioner': {'power_range': (800, 2000), 'pattern': 'steady'},
            'Water Heater (Geyser)': {'power_range': (1000, 2000), 'pattern': 'intermittent'},
            'Refrigerator': {'power_range': (100, 300), 'pattern': 'cyclic'},
            'Washing Machine': {'power_range': (300, 500), 'pattern': 'variable'},
            'Microwave': {'power_range': (800, 1200), 'pattern': 'burst'},
            'Iron Box': {'power_range': (750, 1000), 'pattern': 'steady'},
            'Television': {'power_range': (50, 150), 'pattern': 'steady'},
            'Fan': {'power_range': (50, 75), 'pattern': 'steady'},
            'LED Lights': {'power_range': (5, 20), 'pattern': 'steady'},
            'Laptop/Computer': {'power_range': (30, 100), 'pattern': 'variable'},
            'Electric Kettle': {'power_range': (1000, 1500), 'pattern': 'burst'},
            'Mixer/Grinder': {'power_range': (400, 750), 'pattern': 'burst'}
        }
    
    def extract_features(self, power_readings, voltage_readings):
        """
        Extract features from power consumption data for appliance detection
        
        Args:
            power_readings: List of power values in kW
            voltage_readings: List of voltage values in V
        
        Returns:
            Feature vector for classification
        """
        power_array = np.array(power_readings)
        voltage_array = np.array(voltage_readings)
        
        features = {
            'mean_power': np.mean(power_array),
            'max_power': np.max(power_array),
            'min_power': np.min(power_array),
            'std_power': np.std(power_array),
            'power_range': np.max(power_array) - np.min(power_array),
            'mean_voltage': np.mean(voltage_array),
            'power_trend': self._calculate_trend(power_array),
            'cyclic_pattern': self._detect_cycles(power_array),
            'burst_count': self._count_bursts(power_array),
            'steady_state': self._is_steady(power_array)
        }
        
        return list(features.values())
    
    def _calculate_trend(self, data):
        """Calculate if power is increasing, decreasing, or steady"""
        if len(data) < 2:
            return 0
        return (data[-1] - data[0]) / len(data)
    
    def _detect_cycles(self, data):
        """Detect cyclic patterns (like refrigerator compressor)"""
        if len(data) < 5:
            return 0
        
        # Simple autocorrelation to detect periodicity
        mean = np.mean(data)
        variance = np.var(data)
        if variance == 0:
            return 0
        
        autocorr = np.correlate(data - mean, data - mean, mode='same')
        return np.max(autocorr) / (len(data) * variance)
    
    def _count_bursts(self, data, threshold=0.5):
        """Count sudden power spikes (like microwave, kettle)"""
        if len(data) < 2:
            return 0
        
        diff = np.diff(data)
        bursts = np.sum(np.abs(diff) > threshold)
        return bursts
    
    def _is_steady(self, data):
        """Check if power consumption is steady"""
        std = np.std(data)
        mean = np.mean(data)
        if mean == 0:
            return 1
        return 1 - min(std / mean, 1)  # Coefficient of variation (inverted)
    
    def detect_appliances(self, power_readings, voltage_readings):
        """
        Detect which appliances are likely running
        
        Args:
            power_readings: Recent power consumption values in WATTS (already converted)
            voltage_readings: Recent voltage values
        
        Returns:
            List of detected appliances with confidence scores
        """
        if len(power_readings) < 5:
            return []
        
        detected = []
        current_power_watts = np.mean(power_readings[-5:])  # Average of last 5 readings in Watts
        
        # Rule-based detection for demo (can be replaced with ML model later)
        for appliance, profile in self.appliance_profiles.items():
            min_power, max_power = profile['power_range']
            
            if min_power <= current_power_watts <= max_power:
                # Calculate confidence based on pattern match
                confidence = self._calculate_confidence(
                    power_readings, 
                    voltage_readings, 
                    profile
                )
                
                if confidence > 0.5:  # 50% threshold
                    detected.append({
                        'appliance': appliance,
                        'confidence': round(confidence * 100, 1),
                        'estimated_power': round(current_power_watts, 2),
                        'cost_per_hour': round((current_power_watts / 1000) * 6.5, 2)  # Convert to kW, then calc cost
                    })
        
        # Sort by confidence
        detected.sort(key=lambda x: x['confidence'], reverse=True)
        return detected[:3]  # Return top 3 matches
    
    def _calculate_confidence(self, power_data, voltage_data, profile):
        """Calculate confidence score for appliance detection"""
        features = self.extract_features(power_data, voltage_data)
        
        # Simple heuristic scoring
        confidence = 0.5  # Base confidence
        
        # Pattern matching
        if profile['pattern'] == 'steady' and features[9] > 0.8:
            confidence += 0.3
        elif profile['pattern'] == 'cyclic' and features[7] > 0.5:
            confidence += 0.3
        elif profile['pattern'] == 'burst' and features[8] > 2:
            confidence += 0.3
        elif profile['pattern'] == 'intermittent' and features[4] > 0.3:
            confidence += 0.2
        
        # Voltage stability (quality check)
        if 220 <= features[5] <= 240:
            confidence += 0.1
        
        return min(confidence, 0.99)
    
    def get_energy_saving_tips(self, detected_appliances):
        """
        Provide personalized energy-saving recommendations
        """
        tips = []
        
        for item in detected_appliances:
            appliance = item['appliance']
            
            if appliance == 'Air Conditioner':
                tips.append({
                    'appliance': appliance,
                    'tip': 'Set AC to 24°C instead of 18°C to save up to 30% energy',
                    'potential_savings': '₹300-500/month'
                })
            elif appliance == 'Water Heater (Geyser)':
                tips.append({
                    'appliance': appliance,
                    'tip': 'Use timer to heat water only 30 mins before bath',
                    'potential_savings': '₹150-250/month'
                })
            elif appliance == 'Refrigerator':
                tips.append({
                    'appliance': appliance,
                    'tip': 'Clean condenser coils monthly and avoid overfilling',
                    'potential_savings': '₹50-100/month'
                })
        
        return tips


# Demo function for testing
def demo_appliance_detection():
    """Demo function to show appliance detection in action"""
    detector = ApplianceDetector()
    
    # Simulate power readings (in kW)
    # Example: AC running (1.5 kW steady)
    power_readings = [1.48, 1.52, 1.50, 1.49, 1.51, 1.50, 1.52, 1.48, 1.51, 1.50]
    voltage_readings = [230, 232, 231, 230, 229, 231, 230, 232, 231, 230]
    
    detected = detector.detect_appliances(power_readings, voltage_readings)
    
    print("🔍 Detected Appliances:")
    print("=" * 60)
    for item in detected:
        print(f"✓ {item['appliance']}")
        print(f"  Confidence: {item['confidence']}%")
        print(f"  Power: {item['estimated_power']} W")
        print(f"  Cost: ₹{item['cost_per_hour']}/hour")
        print()
    
    tips = detector.get_energy_saving_tips(detected)
    print("\n💡 Energy Saving Tips:")
    print("=" * 60)
    for tip in tips:
        print(f"📌 {tip['appliance']}")
        print(f"   {tip['tip']}")
        print(f"   Potential Savings: {tip['potential_savings']}")
        print()


if __name__ == '__main__':
    demo_appliance_detection()
