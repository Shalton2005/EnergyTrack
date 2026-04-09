"""
EnergyTrack - Run Application
Quick launcher script with pre-flight checks
"""
import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - MISSING")
        return False

def print_banner():
    """Print application banner"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║              🏠 EnergyTrack 🔋                          ║
    ║        Smart Energy Monitoring System                   ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

def main():
    """Main function"""
    print_banner()
    
    print("Pre-flight checks...")
    print("=" * 60)
    
    all_ok = True
    
    # Check critical files
    all_ok &= check_file_exists('app.py', 'Main application')
    all_ok &= check_file_exists('config.py', 'Configuration file')
    all_ok &= check_file_exists('.env', 'Environment variables')
    all_ok &= check_file_exists('requirements.txt', 'Dependencies list')
    
    # Check modules
    all_ok &= check_file_exists('models/database.py', 'Database models')
    all_ok &= check_file_exists('auth/routes.py', 'Authentication routes')
    all_ok &= check_file_exists('dashboard/routes.py', 'Dashboard routes')
    all_ok &= check_file_exists('admin/routes.py', 'Admin routes')
    
    # Check ML
    all_ok &= check_file_exists('ml/predictor.py', 'ML predictor')
    all_ok &= check_file_exists('ml/device_identifier.py', 'Device identifier')
    
    # Check optional files
    has_dataset = check_file_exists('dataset.csv', 'Sample dataset')
    has_model = check_file_exists('model.pkl', 'Trained ML model')
    
    print("=" * 60)
    
    if not all_ok:
        print("\n❌ Some critical files are missing!")
        print("Please run: python setup.py")
        sys.exit(1)
    
    if not has_dataset:
        print("\n⚠️  Dataset not found. Generating now...")
        os.system('python generate_dataset.py')
    
    if not has_model:
        print("\n⚠️  ML model not found. Training now...")
        os.system('python -c "from ml.predictor import train_model_script; train_model_script()"')
    
    print("\n✅ All checks passed!")
    print("=" * 60)
    print("\n🚀 Starting EnergyTrack...")
    print("\nAdmin bootstrap is environment-driven.")
    print("Set ADMIN_EMAIL and ADMIN_PASSWORD in .env before first run.")
    print("\nApplication will start at: http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    
    # Import and run app
    try:
        from app import create_app
        app = create_app()
        app.run(debug=app.config.get('FLASK_DEBUG', False), host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error starting application: {e}")
        print("\nPlease check:")
        print("1. All dependencies are installed: pip install -r requirements.txt")
        print("2. .env file is properly configured")
        print("3. Python version is 3.8 or higher")
        sys.exit(1)

if __name__ == '__main__':
    main()
