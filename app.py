"""
Main Flask application for EnergyTrack
Energy Monitoring and Prediction System
"""
from flask import Flask, render_template, send_file
from flask_login import LoginManager, current_user
from flask_mail import Mail
from models.database import db, User
from config import Config
from datetime import datetime

# Initialize extensions
login_manager = LoginManager()
mail = Mail()


def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Initialize mail only if configured
    try:
        mail.init_app(app)
    except:
        print("Warning: Flask-Mail not configured. Email features disabled.")
    
    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from auth.routes import auth_bp
    from dashboard.routes import dashboard_bp
    from support.routes import support_bp
    from devices.routes import devices_bp
    from payment.routes import payment_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(support_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(payment_bp)
    
    # Home route
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            # Regular users go to dashboard
            return render_template('dashboard/index.html')
        return render_template('home.html')
    
    # Download report route
    @app.route('/download-report')
    def download_report():
        from flask_login import login_required
        from models.database import ConsumptionLog
        from ml.predictor import EnergyPredictor
        from utils.pdf_generator import generate_monthly_report
        
        if not current_user.is_authenticated:
            return "Unauthorized", 401
        
        # Get monthly data
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        logs = ConsumptionLog.query.filter(
            ConsumptionLog.user_id == current_user.id,
            ConsumptionLog.timestamp >= month_start
        ).all()
        
        monthly_kwh = sum([log.global_active_power for log in logs]) / 60 if logs else 0
        
        # Calculate bill
        predictor = EnergyPredictor()
        bill_details = predictor.calculate_bill(monthly_kwh, current_user.get_tariff())
        
        # Generate PDF
        pdf_buffer = generate_monthly_report(current_user, monthly_kwh, bill_details, logs)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'energy_report_{datetime.now().strftime("%Y%m")}.pdf',
            mimetype='application/pdf'
        )
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500
    
    # Template context processors
    @app.context_processor
    def utility_processor():
        return {
            'now': datetime.now(),
            'app_name': 'EnergyTrack'
        }
    
    # Create database tables
    with app.app_context():
        db.create_all()

        # Optionally bootstrap an admin account from environment settings.
        admin_email = app.config.get('ADMIN_EMAIL')
        admin_password = app.config.get('ADMIN_PASSWORD')
        if admin_email and admin_password:
            admin = User.query.filter_by(email=admin_email).first()
            if not admin:
                admin = User(
                    name='System Administrator',
                    email=admin_email,
                    is_verified=True,
                    is_admin=True,
                    plan_type=None
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                print(f"Admin user created: {admin_email}")
        else:
            print("Admin bootstrap skipped. Set ADMIN_EMAIL and ADMIN_PASSWORD in .env to create one.")
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("⚡ ENERGYTRACK - USER APPLICATION")
    print("="*60)
    print("\n🌐 User Application URL:")
    print("   Local:    http://127.0.0.1:5000")
    print("   Network:  http://[YOUR_IP]:5000")
    print("\n📱 For Clients on Same WiFi:")
    print("   Use:      http://[YOUR_IP]:5000")
    print("   Find IP:  ipconfig (Windows) or ifconfig (Linux/Mac)")
    print("\n🔐 Admin Portal (Separate Application):")
    print("   Run:      python admin_app.py")
    print("   URL:      http://127.0.0.1:5001")
    print("\n👤 Demo Accounts:")
    print(f"   User:     Register at /auth/register")
    print(f"   Admin:    Access admin portal at http://127.0.0.1:5001")
    print("="*60 + "\n")
    app.run(debug=app.config.get('FLASK_DEBUG', False), host='0.0.0.0', port=5000)
