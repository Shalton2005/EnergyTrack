# EnergyTrack - Quick Start Guide

## âš¡ Fast Setup (5 Minutes)

### 1ï¸âƒ£ Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2ï¸âƒ£ Run Setup Script
```powershell
python setup.py
```

This automatically:
- Checks Python version
- Installs dependencies
- Creates .env file
- Generates sample dataset
- Trains ML model

### 3ï¸âƒ£ Configure Email (Optional but Recommended)

Edit `.env` file:
```env
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
```

**For Gmail:**
1. Enable 2-Step Verification
2. Go to: https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"
4. Paste in .env

### 4ï¸âƒ£ Start Application
```powershell
python app.py
```

### 5ï¸âƒ£ Access Application

Open browser: **http://127.0.0.1:5000**

## ðŸ”‘ Default Login

**Admin Account:**
- Email: `admin@example.com`
- Password: `replace-with-strong-password`

**âš ï¸ CHANGE PASSWORD AFTER FIRST LOGIN!**

## ðŸ“± Quick Test

1. **Register New User**
   - Click "Get Started"
   - Fill form and submit
   - Check console for OTP (if email not configured)
   - Verify and login

2. **View Dashboard**
   - See real-time data streaming
   - Watch charts update every 5 seconds
   - Check voltage and power readings

3. **Check Billing**
   - View current month consumption
   - See tariff breakdown
   - Check cost predictions

4. **Test Admin Panel**
   - Login as admin
   - Click "Admin Panel"
   - View all users and system stats

## ðŸŽ¯ Key URLs

- **Home**: http://127.0.0.1:5000/
- **Login**: http://127.0.0.1:5000/auth/login
- **Dashboard**: http://127.0.0.1:5000/dashboard/
- **Admin**: http://127.0.0.1:5000/admin/

## ðŸ†˜ Troubleshooting

### Email not working?
Skip OTP verification for now - check console for OTP code

### Model not found?
```powershell
python -c "from ml.predictor import train_model_script; train_model_script()"
```

### Dataset missing?
```powershell
python generate_dataset.py
```

### Port already in use?
Edit `app.py` line 105, change port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## ðŸ“š Need More Info?

See **README.md** for complete documentation!

---

**Ready to monitor your energy! ðŸ âš¡**

