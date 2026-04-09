"""
Configuration file for EnergyTrack application
"""
import os
import secrets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_urlsafe(32)
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail configuration (optional)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')  # Empty = disabled
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@energytrack.app')
    MAIL_SUPPRESS_SEND = False  # Allow sending emails when configured
    
    # Admin credentials
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@energytrack.local')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')
    
    # ML Model
    MODEL_PATH = 'model.pkl'
    DATASET_PATH = 'dataset.csv'
    
    # Simulation settings
    SIMULATION_INTERVAL = 5  # seconds between data points
    
    # Alert thresholds
    VOLTAGE_MIN = 220
    VOLTAGE_MAX = 240
    POWER_SPIKE_THRESHOLD = 5.0  # kW
    HIGH_CONSUMPTION_THRESHOLD = 200  # kWh per month
