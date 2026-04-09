"""
Generate sample India smart-meter dataset for EnergyTrack
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_dataset(num_records=10000):
    """Generate realistic smart meter data"""
    print("Generating India smart-meter dataset...")
    
    # Start date
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    
    # Lists to store data
    data = {
        'datetime': [],
        'global_active_power': [],
        'voltage': [],
        'current': [],
        'sub_metering1': [],
        'sub_metering2': [],
        'sub_metering3': []
    }
    
    # Base consumption patterns (kW)
    base_consumption = {
        'night': (0.2, 0.8),      # 00:00 - 06:00
        'morning': (1.5, 3.5),    # 06:00 - 10:00
        'day': (0.8, 2.0),        # 10:00 - 18:00
        'evening': (2.0, 4.5),    # 18:00 - 23:00
    }
    
    current_time = start_date
    
    for i in range(num_records):
        hour = current_time.hour
        
        # Determine time period
        if 0 <= hour < 6:
            period = 'night'
        elif 6 <= hour < 10:
            period = 'morning'
        elif 10 <= hour < 18:
            period = 'day'
        else:
            period = 'evening'
        
        # Generate realistic power consumption
        min_power, max_power = base_consumption[period]
        base_power = random.uniform(min_power, max_power)
        
        # Add some random variations
        power_variation = random.gauss(0, 0.2)
        power = max(0.1, base_power + power_variation)
        
        # Generate voltage (typical India voltage with variations)
        voltage = random.gauss(230, 5)  # 230V ± 5V
        
        # Occasional voltage fluctuations
        if random.random() < 0.05:  # 5% chance
            voltage += random.choice([-15, 15])
        
        voltage = max(200, min(250, voltage))
        
        # Calculate current (P = V * I * power_factor)
        power_factor = random.uniform(0.85, 0.95)
        current = (power * 1000) / (voltage * power_factor)
        
        # Sub-metering (distribute total power)
        # Sub-meter 1: Kitchen appliances & lighting (30-40%)
        # Sub-meter 2: Water heater & AC (40-50%)
        # Sub-meter 3: Other appliances (20-30%)
        
        total_wh = power * 1000  # Convert kW to W
        
        sub1_percent = random.uniform(0.30, 0.40)
        sub2_percent = random.uniform(0.40, 0.50)
        sub3_percent = 1.0 - sub1_percent - sub2_percent
        
        sub_metering1 = total_wh * sub1_percent
        sub_metering2 = total_wh * sub2_percent
        sub_metering3 = total_wh * sub3_percent
        
        # Store data
        data['datetime'].append(current_time)
        data['global_active_power'].append(round(power, 3))
        data['voltage'].append(round(voltage, 1))
        data['current'].append(round(current, 2))
        data['sub_metering1'].append(round(sub_metering1, 1))
        data['sub_metering2'].append(round(sub_metering2, 1))
        data['sub_metering3'].append(round(sub_metering3, 1))
        
        # Increment time (1 minute intervals)
        current_time += timedelta(minutes=1)
        
        # Progress indicator
        if (i + 1) % 1000 == 0:
            print(f"Generated {i + 1}/{num_records} records...")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_file = 'dataset.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\nDataset created successfully!")
    print(f"File: {output_file}")
    print(f"Records: {len(df)}")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print("\nSample data:")
    print(df.head(10))
    print("\nStatistics:")
    print(df.describe())
    
    return df


if __name__ == '__main__':
    # Generate 10,000 records (approximately 1 week of minute-by-minute data)
    generate_dataset(10000)
