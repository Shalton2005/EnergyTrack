# ðŸš€ Getting Started with EnergyTrack

## Welcome to EnergyTrack!

This is your complete guide to get EnergyTrack up and running in minutes.

## ðŸ“‹ Prerequisites

Before you begin, make sure you have:
- âœ… Python 3.8 or higher installed
- âœ… pip (Python package manager)
- âœ… Internet connection (for downloading packages)
- âœ… A text editor (VS Code, Notepad++, etc.)

## ðŸŽ¯ Three Ways to Start

### Method 1: Super Quick Start (Recommended) âš¡

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the launcher (does everything automatically)
python run.py
```

That's it! The application will:
- âœ… Check all files
- âœ… Generate dataset if missing
- âœ… Train ML model if needed
- âœ… Start the server

### Method 2: Automated Setup ðŸ”§

```powershell
# 1. Run setup script (one-time)
python setup.py

# 2. Start application
python app.py
```

### Method 3: Manual Setup ðŸ› ï¸

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate dataset
python generate_dataset.py

# 3. Train ML model
python -c "from ml.predictor import train_model_script; train_model_script()"

# 4. Start application
python app.py
```

## ðŸŒ Access the Application

Once running, open your browser to:
```
http://127.0.0.1:5000
```

## ðŸ”‘ Login Credentials

### Admin Account (Pre-created)
- **Email:** admin@example.com
- **Password:** replace-with-strong-password

âš ï¸ **IMPORTANT:** Change this password immediately after first login!

### Create User Account
1. Click "Get Started" on home page
2. Fill registration form
3. Verify email with OTP (check console if email not configured)
4. Login with your credentials

## ðŸ“§ Email Configuration (Optional but Recommended)

For OTP verification to work via email:

1. **Edit `.env` file**

2. **For Gmail:**
```env
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-16-character-app-password
```

3. **Get Gmail App Password:**
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification"
   - Go to "App passwords"
   - Generate password for "Mail"
   - Copy and paste in `.env`

4. **Restart application** for changes to take effect

## ðŸŽ® First Steps After Login

### For Regular Users:

1. **Dashboard** ðŸ“Š
   - View live energy consumption
   - Monitor voltage in real-time
   - See today's usage
   - Check monthly estimates

2. **Billing** ðŸ’°
   - Review current month consumption
   - See detailed cost breakdown
   - Understand tariff slabs

3. **Alerts** ðŸ””
   - Check voltage fluctuation warnings
   - Review power spike alerts
   - Manage notifications

4. **Device Identification** ðŸ”Œ
   - See which appliances are active
   - View estimated power per device

5. **Settings** âš™ï¸
   - Change password
   - Update tariff rates
   - Configure alert preferences

6. **Download Report** ðŸ“„
   - Click "Download Report (PDF)"
   - Get comprehensive monthly analysis

### For Admins:

1. **Admin Panel** (sidebar menu)
   - View system statistics
   - Monitor all users
   - Check total consumption

2. **User Management**
   - View all registered users
   - See user consumption stats
   - Delete accounts if needed
   - View individual user logs

## ðŸŽ¯ Quick Feature Tour

### Real-time Monitoring
- Data updates every 5 seconds
- Live charts show power and voltage
- Color-coded alerts for anomalies

### ML Predictions
- Next 15-minute consumption forecast
- Daily total estimation
- Monthly bill prediction
- Accurate tariff calculations

### Smart Alerts
- Voltage too low/high? Get notified!
- Sudden power spike? Alert triggered!
- Monthly bill exceeding budget? Warning sent!

### Device Detection (NILM)
- Identifies 8 common appliances
- Based on power consumption patterns
- Shows confidence level
- Real-time updates

## ðŸ”§ Customization

### Change Tariff Rates

Go to **Settings** â†’ **Tariff Configuration**

Edit JSON:
```json
{
  "fixed_charges": 100,
  "slabs": [
    {"up_to": 50, "rate": 3.40},
    {"up_to": 100, "rate": 4.95},
    {"up_to": 200, "rate": 6.50},
    {"above": 200, "rate": 7.55}
  ]
}
```

### Toggle Dark Mode

Click the moon/sun icon (bottom-right corner)
- Preference saved automatically
- Works across all pages

### Configure Alerts

Go to **Settings** â†’ **Alert Preferences**
- Enable/disable voltage alerts
- Toggle bill prediction alerts
- Control email notifications

## ðŸ“± Mobile Access

EnergyTrack is fully responsive! Access from:
- ðŸ“± Smartphones
- ðŸ“± Tablets
- ðŸ’» Laptops
- ðŸ–¥ï¸ Desktops

## ðŸ†˜ Troubleshooting

### Problem: Can't access http://127.0.0.1:5000

**Solution:**
- Check if application is running
- Try http://localhost:5000
- Check firewall settings

### Problem: "Module not found" error

**Solution:**
```powershell
pip install -r requirements.txt
```

### Problem: OTP not received

**Solution:**
- Check console output (OTP printed there)
- Configure email in `.env`
- Verify MAIL_USERNAME and MAIL_PASSWORD

### Problem: Database error

**Solution:**
```powershell
# Delete database and restart (creates new one)
Remove-Item database.db
python app.py
```

### Problem: Model not found

**Solution:**
```powershell
python -c "from ml.predictor import train_model_script; train_model_script()"
```

### Problem: Dataset missing

**Solution:**
```powershell
python generate_dataset.py
```

### Problem: Port already in use

**Solution:**
Edit `app.py` (line ~105):
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001
```

## ðŸŽ“ Learning Path

1. **Day 1:** Register, explore dashboard, understand readings
2. **Day 2:** Configure tariff, check billing, download report
3. **Day 3:** Set up alerts, test device identification
4. **Day 4:** Explore admin panel (if admin)
5. **Day 5:** Customize settings, understand ML predictions

## ðŸ“š Documentation

- **README.md** - Complete documentation
- **QUICKSTART.md** - Fast setup guide
- **PROJECT_SUMMARY.md** - Technical overview
- **This file** - User getting started guide

## ðŸ’¡ Tips & Tricks

1. **Dark Mode** - Better for nighttime viewing
2. **Live Charts** - Auto-refresh, no manual reload needed
3. **PDF Reports** - Download monthly for record-keeping
4. **Device ID** - More accurate over time as system learns
5. **Tariff Updates** - Update quarterly when rates change

## ðŸŽ‰ You're Ready!

Everything you need to know to start monitoring your energy consumption intelligently.

### Quick Commands Reference

```powershell
# Start application (easy way)
python run.py

# Start application (standard way)
python app.py

# Generate new dataset
python generate_dataset.py

# Retrain ML model
python -c "from ml.predictor import train_model_script; train_model_script()"

# Run setup
python setup.py
```

## ðŸŒŸ Next Steps

- Explore all features
- Configure your tariff
- Set up email notifications
- Download your first report
- Invite family members to register

---

**Need Help?** Check README.md for detailed documentation

**Found a Bug?** Review code comments and error messages

**Want to Customize?** All code is well-commented and modular

---

## ðŸ Ready to Go!

Start with:
```powershell
python run.py
```

Then visit: **http://127.0.0.1:5000**

Happy Energy Monitoring! âš¡ðŸ 

---

*EnergyTrack - Making Energy Monitoring Simple and Smart*

