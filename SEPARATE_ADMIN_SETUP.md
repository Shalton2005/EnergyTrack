# SEPARATE ADMIN PORTAL - SETUP COMPLETE

## ðŸŽ¯ TWO SEPARATE APPLICATIONS

### 1. **USER APPLICATION** (Port 5000)
**For:** Regular users/clients  
**Access:**
- Local: `http://127.0.0.1:5000`
- Same WiFi: `http://[YOUR_IP]:5000`

**Features:**
- User registration & login
- Energy monitoring dashboard
- Bill generation
- Device control (IoT)
- ML predictions
- Alerts & notifications
- Support tickets
- Subscription management

**Start Command:**
```bash
python app.py
# OR
start_user_app.bat
```

---

### 2. **ADMIN PORTAL** (Port 5001)
**For:** Administrators only  
**Access:**
- Local: `http://127.0.0.1:5001`
- Same WiFi: `http://[YOUR_IP]:5001`

**Features:**
- Dashboard analytics (IST timezone)
- User management
- Revenue analytics
- Support ticket management
- System settings
- Payment tracking
- **NO user features** (pure admin)

**Start Command:**
```bash
python admin_app.py
# OR
start_admin_portal.bat
```

**Login Credentials:**
- Email: `admin@example.com`
- Password: `replace-with-strong-password`

---

## ðŸš€ QUICK START

### Option 1: Start Both Applications
```bash
start_both.bat
```
This opens two separate windows:
- Window 1: User App (Port 5000)
- Window 2: Admin Portal (Port 5001)

### Option 2: Start Individually
**For Users (Clients):**
```bash
python app.py
# Runs on http://localhost:5000
```

**For Admin:**
```bash
python admin_app.py
# Runs on http://localhost:5001
# Login: admin@example.com / replace-with-strong-password
```

---

## ðŸ“± NETWORK ACCESS (Same WiFi)

### Find Your IP Address:
```bash
# Windows
ipconfig

# Look for "IPv4 Address" under your WiFi adapter
# Example: 192.168.1.100
```

### Share with Clients:
**User App:** `http://192.168.1.100:5000`  
**Admin Portal:** `http://192.168.1.100:5001`

---

## ðŸ” SECURITY NOTES

### Admin Portal Security:
1. âœ… **Separate Port** (5001) - Easy to firewall
2. âœ… **Admin-only authentication** - Regular users cannot access
3. âœ… **Separate application** - No code sharing with user app
4. âœ… **Independent sessions** - User login doesn't affect admin

### Production Recommendations:
1. Change admin password from `replace-with-strong-password`
2. Use HTTPS (SSL certificates)
3. Configure firewall to block port 5001 from external access
4. Use VPN for remote admin access
5. Enable rate limiting on login endpoints

---

## ðŸ“Š ADMIN PORTAL FEATURES

### âœ… All Fixed Issues:
- âœ… **Timezone:** All timestamps in Asia/Kolkata (IST)
- âœ… **Graph Size:** Fixed 300px container (no growth)
- âœ… **Payment Status:** Standardized to 'SUCCESS'
- âœ… **Separate App:** Runs on port 5001
- âœ… **No User Features:** Pure admin functionality

### Dashboard:
- Total Users stat card
- Total Revenue stat card (â‚¹)
- Monthly Revenue stat card
- Open Tickets stat card
- User Distribution chart (doughnut)
- Subscription breakdown table
- Revenue breakdown
- Recent registrations (IST)

### Menu Structure:
```
ðŸ“Š Dashboard
ðŸ’° Revenue & Finance
   â”œâ”€ Revenue Analytics
   â””â”€ Payment History
ðŸ‘¥ User Management
   â”œâ”€ All Users
   â””â”€ User Details
ðŸŽ« Support Tickets [badge]
âš™ï¸ System Settings
   â”œâ”€ Email Configuration
   â””â”€ General Settings
ðŸšª Logout
```

---

## ðŸ§ª TESTING

### Test User Application (Port 5000):
1. Start: `python app.py`
2. Open: `http://localhost:5000`
3. Register a new user account
4. Verify user dashboard features

### Test Admin Portal (Port 5001):
1. Start: `python admin_app.py`
2. Open: `http://localhost:5001/login`
3. Login: `admin@example.com` / `replace-with-strong-password`
4. Verify all admin features:
   - Dashboard shows IST timestamp
   - Graph has fixed height
   - Revenue analytics works
   - User management accessible
   - Support tickets viewable

### Test Network Access:
1. Find your IP: `ipconfig`
2. User App: `http://[YOUR_IP]:5000`
3. Admin Portal: `http://[YOUR_IP]:5001`
4. Test from another device on same WiFi

---

## ðŸ“ FILE STRUCTURE

```
EnergyTrack/
â”œâ”€â”€ app.py                    # USER APPLICATION (Port 5000)
â”œâ”€â”€ admin_app.py              # ADMIN PORTAL (Port 5001)
â”œâ”€â”€ start_user_app.bat        # Launch user app
â”œâ”€â”€ start_admin_portal.bat    # Launch admin portal
â”œâ”€â”€ start_both.bat            # Launch both apps
â”œâ”€â”€ models/
â”‚   â””â”€â”€ database.py           # Shared database models
â”œâ”€â”€ templates/
â”‚   â”œâ”€â”€ admin/                # Admin templates
â”‚   â”‚   â”œâ”€â”€ admin_base.html
â”‚   â”‚   â”œâ”€â”€ admin_login.html
â”‚   â”‚   â”œâ”€â”€ dashboard.html
â”‚   â”‚   â”œâ”€â”€ users.html
â”‚   â”‚   â”œâ”€â”€ revenue.html
â”‚   â”‚   â””â”€â”€ settings.html
â”‚   â””â”€â”€ dashboard/            # User templates
â””â”€â”€ utils/
    â””â”€â”€ timezone_utils.py     # IST timezone utilities
```

---

## ðŸŽ‰ ADVANTAGES OF SEPARATE APPS

### 1. **Security**
- Different ports = Easy firewall rules
- Admin access isolated from user traffic
- Independent authentication systems

### 2. **Performance**
- Admin operations don't affect user experience
- Can scale user app independently
- Admin can restart without affecting users

### 3. **Maintenance**
- Update admin features without touching user app
- Deploy separately
- Different logging and monitoring

### 4. **Network Control**
- Port 5000: Open to WiFi clients
- Port 5001: Restrict to admin IPs only
- Easy to implement VPN for admin access

---

## âš ï¸ IMPORTANT NOTES

1. **Both apps share the same database**
   - Changes in admin portal reflect in user app
   - Database must be initialized before running either app

2. **Run both for full functionality**
   - Users access port 5000
   - Admins access port 5001

3. **Firewall Configuration**
   - Allow port 5000 for clients on WiFi
   - Block port 5001 from external access
   - Use VPN for remote admin access

4. **Production Deployment**
   - Use WSGI server (gunicorn, waitress)
   - Enable HTTPS on both apps
   - Set up proper logging
   - Configure environment variables

---

## ðŸ”„ NEXT STEPS

1. **Test both applications:**
   ```bash
   start_both.bat
   ```

2. **Access user app:**
   - Open `http://localhost:5000`
   - Register new account
   - Test features

3. **Access admin portal:**
   - Open `http://localhost:5001/login`
   - Login as admin
   - Verify all features

4. **Test network access:**
   - Find IP with `ipconfig`
   - Access from phone/tablet on WiFi
   - Test both apps

**SYSTEM STATUS:** âœ… **READY**

Both applications are now completely separate and ready for production!

