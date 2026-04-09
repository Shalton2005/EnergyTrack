"""
Quick Setup Script for EnergyTrack
Run this script to set up the application
"""
import os
import sys
import subprocess

def print_step(step, message):
    """Print formatted step message"""
    print(f"\n{'='*60}")
    print(f"Step {step}: {message}")
    print('='*60)

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n→ {description}...")
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {description} failed")
        print(f"  {str(e)}")
        return False

def main():
    """Main setup function"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║           EnergyTrack Setup Script                      ║
    ║           Smart Energy Monitoring System                ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check Python version
    print_step(1, "Checking Python version")
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("✗ Error: Python 3.8 or higher is required")
        sys.exit(1)
    print("✓ Python version is compatible")
    
    # Step 2: Install dependencies
    print_step(2, "Installing Python dependencies")
    if not run_command("pip install -r requirements.txt", "Installing packages"):
        print("\nIf installation failed, try:")
        print("  pip install --upgrade pip")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 3: Create .env file
    print_step(3, "Setting up environment variables")
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            try:
                with open('.env.example', 'r') as f:
                    env_content = f.read()
                with open('.env', 'w') as f:
                    f.write(env_content)
                print("✓ Created .env file from .env.example")
                print("\n⚠ IMPORTANT: Edit .env file to configure email settings!")
            except Exception as e:
                print(f"✗ Error creating .env file: {e}")
        else:
            print("✗ .env.example not found")
    else:
        print("✓ .env file already exists")
    
    # Step 4: Generate dataset
    print_step(4, "Generating sample dataset")
    if not os.path.exists('dataset.csv'):
        if run_command("python generate_dataset.py", "Generating dataset"):
            print("✓ Dataset created successfully")
        else:
            print("⚠ Dataset generation failed, but you can continue")
    else:
        print("✓ Dataset already exists")
    
    # Step 5: Train ML model
    print_step(5, "Training ML model")
    if not os.path.exists('model.pkl'):
        train_cmd = 'python -c "from ml.predictor import train_model_script; train_model_script()"'
        if run_command(train_cmd, "Training model"):
            print("✓ Model trained successfully")
        else:
            print("⚠ Model training failed, but you can continue")
    else:
        print("✓ Model already exists")
    
    # Step 6: Create necessary directories
    print_step(6, "Creating directories")
    directories = ['static', 'static/css', 'static/js', 'static/images']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✓ Directories created")
    
    # Final instructions
    print("\n" + "="*60)
    print("Setup completed successfully! 🎉")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit .env file and configure your email settings")
    print("2. Run the application:")
    print("   python app.py")
    print("\n3. Open your browser and visit:")
    print("   http://127.0.0.1:5000")
    print("\n4. Configure admin bootstrap in .env:")
    print("   ADMIN_EMAIL=admin@energytrack.local")
    print("   ADMIN_PASSWORD=replace-with-strong-password")
    print("\n5. Install Git before using daily push workflow")
    print("\n⚠ Use strong secrets before production deployment.")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        sys.exit(1)
