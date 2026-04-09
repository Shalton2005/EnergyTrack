"""
Machine Learning module for energy consumption prediction
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os
from datetime import datetime, timedelta


class EnergyPredictor:
    """ML model for energy consumption prediction"""
    
    def __init__(self, model_path='model.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        
    def load_model(self):
        """Load trained model from disk"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
                self.feature_columns = data['feature_columns']
            return True
        return False
    
    def save_model(self):
        """Save trained model to disk"""
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns
            }, f)
    
    def prepare_features(self, df):
        """Extract features from dataset"""
        df = df.copy()
        
        # Convert datetime to features
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df['hour'] = df['datetime'].dt.hour
            df['day'] = df['datetime'].dt.day
            df['month'] = df['datetime'].dt.month
            df['weekday'] = df['datetime'].dt.weekday
            df['is_weekend'] = df['weekday'].isin([5, 6]).astype(int)
        
        # Feature engineering
        df['total_sub_metering'] = df['sub_metering1'] + df['sub_metering2'] + df['sub_metering3']
        df['power_factor'] = df['global_active_power'] / (df['voltage'] * df['current'] + 0.001)
        
        # Lag features (previous values)
        if len(df) > 1:
            df['power_lag_1'] = df['global_active_power'].shift(1)
            df['power_lag_2'] = df['global_active_power'].shift(2)
        else:
            df['power_lag_1'] = df['global_active_power']
            df['power_lag_2'] = df['global_active_power']
        
        # Fill NaN values
        df = df.fillna(method='bfill').fillna(0)
        
        return df
    
    def train(self, dataset_path):
        """Train the model on historical data"""
        print("Loading dataset...")
        df = pd.read_csv(dataset_path)
        
        print("Preparing features...")
        df = self.prepare_features(df)
        
        # Define feature columns
        self.feature_columns = [
            'voltage', 'current', 'sub_metering1', 'sub_metering2', 'sub_metering3',
            'hour', 'day', 'month', 'weekday', 'is_weekend',
            'total_sub_metering', 'power_factor', 'power_lag_1', 'power_lag_2'
        ]
        
        # Prepare X and y
        X = df[self.feature_columns]
        y = df['global_active_power']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        print("Scaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print("Training Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)
        
        print(f"\nModel Performance:")
        print(f"Train MAE: {mean_absolute_error(y_train, train_pred):.4f}")
        print(f"Test MAE: {mean_absolute_error(y_test, test_pred):.4f}")
        print(f"Train R²: {r2_score(y_train, train_pred):.4f}")
        print(f"Test R²: {r2_score(y_test, test_pred):.4f}")
        
        # Save model
        self.save_model()
        print(f"\nModel saved to {self.model_path}")
        
        return {
            'train_mae': mean_absolute_error(y_train, train_pred),
            'test_mae': mean_absolute_error(y_test, test_pred),
            'train_r2': r2_score(y_train, train_pred),
            'test_r2': r2_score(y_test, test_pred)
        }
    
    def predict_next_consumption(self, current_data):
        """Predict next 15 minutes consumption"""
        if not self.model:
            if not self.load_model():
                return None
        
        # Prepare features
        df = pd.DataFrame([current_data])
        df = self.prepare_features(df)
        
        # Predict
        X = df[self.feature_columns]
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        
        return max(0, prediction)  # Ensure non-negative
    
    def predict_daily_consumption(self, recent_data):
        """Predict total daily consumption (kWh)"""
        if not self.model:
            if not self.load_model():
                return None
        
        # Use recent data to predict hourly for rest of day
        predictions = []
        
        for hour in range(24):
            sample_data = recent_data.copy()
            sample_data['hour'] = hour
            sample_data['datetime'] = datetime.now().replace(hour=hour)
            
            df = pd.DataFrame([sample_data])
            df = self.prepare_features(df)
            
            X = df[self.feature_columns]
            X_scaled = self.scaler.transform(X)
            pred = self.model.predict(X_scaled)[0]
            predictions.append(max(0, pred))
        
        # Convert to kWh (assuming predictions are in kW, aggregate hourly)
        daily_kwh = sum(predictions)
        return daily_kwh
    
    def predict_monthly_consumption(self, daily_average):
        """Predict monthly consumption based on daily average"""
        # Simple estimation: daily average * 30 days
        return daily_average * 30
    
    def calculate_bill(self, monthly_kwh, tariff):
        """Calculate electricity bill based on tariff slabs"""
        total_cost = tariff.get('fixed_charges', 0)
        remaining_units = monthly_kwh
        slab_breakdown = []
        
        for slab in tariff.get('slabs', []):
            if remaining_units <= 0:
                break
            
            if 'up_to' in slab:
                # Units up to this slab limit
                units_in_slab = min(remaining_units, slab['up_to'])
                cost = units_in_slab * slab['rate']
                slab_breakdown.append({
                    'slab': f"0-{slab['up_to']} units",
                    'units': round(units_in_slab, 2),
                    'rate': round(slab['rate'], 2),
                    'cost': round(cost, 2)
                })
                remaining_units -= units_in_slab
            elif 'above' in slab:
                # All remaining units
                cost = remaining_units * slab['rate']
                slab_breakdown.append({
                    'slab': f"Above {slab['above']} units",
                    'units': round(remaining_units, 2),
                    'rate': round(slab['rate'], 2),
                    'cost': round(cost, 2)
                })
                remaining_units = 0
            
            total_cost += cost
        
        return {
            'total_cost': round(total_cost, 2),
            'fixed_charges': round(tariff.get('fixed_charges', 0), 2),
            'energy_charges': round(total_cost - tariff.get('fixed_charges', 0), 2),
            'breakdown': slab_breakdown
        }


def train_model_script(dataset_path='dataset.csv', model_path='model.pkl'):
    """Standalone script to train the model"""
    predictor = EnergyPredictor(model_path)
    metrics = predictor.train(dataset_path)
    return metrics


if __name__ == '__main__':
    # Train model when run directly
    print("EnergyTrack ML Model Training")
    print("=" * 50)
    train_model_script()
