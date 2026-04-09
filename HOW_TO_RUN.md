# âš¡ HOW TO RUN ENERGYTRACK âš¡

## ðŸŽ¯ FASTEST WAY (2 Commands)

Open PowerShell in the EnergyTrack folder and run:

```powershell
pip install -r requirements.txt
python run.py
```

**That's it!** The app will:
1. Check all files
2. Generate dataset (if missing)
3. Train ML model (if missing)
4. Start the server

Then open browser: **http://127.0.0.1:5000**

---

## ðŸ” LOGIN

**Admin Account:**
- Email: `admin@example.com`
- Password: `replace-with-strong-password`

**Or create new account:**
- Click "Get Started"
- Register with your email
- Use OTP from console (if email not configured)

---

## ðŸ“§ EMAIL SETUP (OPTIONAL)

Edit `.env` file:

```env
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
```

**Get Gmail App Password:**
1. Visit: https://myaccount.google.com/apppasswords
2. Generate password
3. Paste in `.env`
4. Restart app

---

## ðŸ›‘ STOP APPLICATION

Press `Ctrl + C` in terminal

---

## ðŸ”„ RESTART

```powershell
python run.py
```

---

## â“ PROBLEMS?

### Can't install packages?
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Port already in use?
Edit `app.py` line 105:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Need fresh start?
```powershell
Remove-Item database.db
Remove-Item model.pkl
Remove-Item dataset.csv
python run.py
```

---

## ðŸ“š DOCUMENTATION

- **GETTING_STARTED.md** - Detailed user guide
- **QUICKSTART.md** - 5-minute setup
- **README.md** - Full documentation
- **PROJECT_SUMMARY.md** - Technical details

---

## âœ… YOU'RE READY!

```powershell
python run.py
```

Visit: **http://127.0.0.1:5000**

Login as admin and explore!

ðŸŽ‰ **Enjoy EnergyTrack!** ðŸŽ‰

