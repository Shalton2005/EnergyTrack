# Testing Guide - Payment Gateway & Bill Generation

## Features Completed âœ…

### 1. Payment Gateway (Dummy Razorpay-style)
- âœ… Upgrade plan page with pricing cards
- âœ… Checkout page with payment method selection (Card/UPI/Net Banking)
- âœ… Payment simulation with success/failure toggle
- âœ… Transaction ID generation
- âœ… Payment success/failure pages
- âœ… Payment history with transaction details
- âœ… Subscription cancellation

### 2. Bill Generation
- âœ… Provider-specific tariff structures (MESCOM, BESCOM, HESCOM, GESCOM, CESC)
- âœ… RR number validation
- âœ… Slab-wise bill calculation
- âœ… Bill preview in web interface
- âœ… PDF bill generation with ReportLab
- âœ… Professional bill formatting

## Testing Instructions

### Test Payment Gateway

1. **Start Application**
   ```
   python app.py
   ```
   Access at: http://127.0.0.1:5000

2. **Register/Login**
   - Register a new user (you'll get 1-month free trial automatically)
   - OR use existing credentials

3. **Test Upgrade Flow**
   - Navigate to **Upgrade Plan** in sidebar
   - You'll see two plans:
     - Premium Monthly: â‚¹99/month
     - Premium Yearly: â‚¹999/year (save â‚¹189)
   
4. **Test Checkout**
   - Click "Upgrade Now" on any plan
   - Select payment method:
     - **Card**: Enter dummy card details (any format)
     - **UPI**: Enter dummy UPI ID
     - **Net Banking**: Select any bank
   
5. **Test Payment Simulation**
   - **Success**: Keep "Simulate Successful Payment" checked â†’ Click Pay
   - **Failure**: Uncheck the checkbox â†’ Click Pay
   
6. **Verify Transaction**
   - Success: Shows transaction ID, updates plan, redirects to success page
   - Failure: Shows error message, no plan change, retry option
   
7. **Check Payment History**
   - Navigate to **Payment History** in sidebar
   - View all transactions with status (SUCCESS/FAILED)
   - See total spent and transaction count

### Test Bill Generation

1. **Ensure User Profile is Complete**
   - User must have:
     - Electricity provider set (MESCOM, BESCOM, etc.)
     - RR Number entered
     - Phone number
   - Go to **Profile** â†’ Update if needed

2. **Generate Bill**
   - Click **Generate Bill** in sidebar
   - View bill preview with:
     - Consumer details
     - Consumption summary
     - Slab-wise breakdown
     - Bill summary (fixed charge + energy charge + tax)

3. **Download PDF**
   - Click **Download PDF** button
   - PDF will download with professional formatting
   - Includes:
     - Provider logo/header
     - Consumer details table
     - Consumption details
     - Slab breakdown table
     - Bill summary
     - Payment information

4. **Verify Bill Calculation**
   - Check if tariff slabs are correct for your provider
   - Verify fixed charges
   - Confirm 5% electricity duty is applied
   - Total = Fixed Charge + Energy Charge + Tax

## Testing Scenarios

### Scenario 1: Free to Premium Upgrade
1. Login as FREE user
2. Navigate to Upgrade Plan
3. Select Premium Monthly
4. Complete payment (simulate success)
5. Verify plan_type updated to PREMIUM_MONTHLY
6. Check IoT Control is now accessible
7. Verify transaction in Payment History

### Scenario 2: Premium Monthly to Yearly Upgrade
1. Login as Premium Monthly user
2. Navigate to Upgrade Plan
3. Select Premium Yearly
4. See "BEST VALUE" badge
5. Complete payment
6. Verify plan_type updated to PREMIUM_YEARLY
7. Check payment history shows both transactions

### Scenario 3: Bill Generation for Different Providers
1. Login as user
2. Go to Profile â†’ Change electricity provider
3. Try each provider:
   - MESCOM: Fixed â‚¹100, slabs 3.40-7.55
   - BESCOM: Fixed â‚¹120, slabs 3.75-7.80
   - HESCOM: Fixed â‚¹110, slabs 3.50-7.60
   - GESCOM: Fixed â‚¹105, slabs 3.45-7.50
   - CESC: Fixed â‚¹125, slabs 3.80-7.85
4. Generate bill for each
5. Verify different tariff structures applied

### Scenario 4: Payment Failure & Retry
1. Navigate to Upgrade Plan
2. Select any plan
3. Uncheck "Simulate Successful Payment"
4. Click Pay
5. Verify failure page shown
6. Click "Try Again"
7. This time check the success checkbox
8. Complete payment successfully

### Scenario 5: Subscription Cancellation
1. Login as Premium user
2. Navigate to Upgrade Plan
3. Scroll to "Cancel Subscription" section
4. Click "Cancel Subscription"
5. Confirm the alert
6. Verify plan_type reverted to FREE
7. Check IoT Control is now restricted

## Key Features to Verify

### Payment Features
- [x] Transaction ID format: TXN-YYYYMMDDHHMMSS-XXXXXX
- [x] Plan type updates in database
- [x] Trial period tracking (trial_ends_at)
- [x] Payment method selection
- [x] GST calculation (18%)
- [x] Success/failure simulation
- [x] Email notification (if email configured)

### Bill Features
- [x] RR number validation (basic format check)
- [x] Provider-specific tariffs loaded
- [x] Slab-wise calculation
- [x] Progressive rate calculation (0-50, 51-100, etc.)
- [x] Fixed charge included
- [x] 5% electricity duty
- [x] PDF generation with tables
- [x] Professional formatting

## Navigation Updates

New sidebar links added:
- **Generate Bill** - Direct link to bill preview
- **Upgrade Plan** - Access subscription upgrade page
- **Payment History** - View all transactions
- **IoT Control** - Premium-only feature (visible to premium users)

Sidebar now shows:
- Plan type badge (FREE/PREMIUM_MONTHLY/PREMIUM_YEARLY)
- Trial days remaining (if in trial period)

## Database Tables Used

### Payment Table
```python
id, user_id, transaction_id, amount, plan_type, 
payment_method, status, payment_date
```

### User Table (Updated Fields)
```python
plan_type, trial_ends_at, phone_number, 
electricity_provider, rr_number
```

## Expected Behavior

### Free Users
- Can view upgrade options
- Cannot access IoT control
- Can generate bills with basic features
- Can view payment history (empty initially)

### Premium Users
- Full access to all features
- IoT device control enabled
- Advanced bill analytics
- Unlimited history
- ML predictions

### Trial Period
- 1 month free trial for all new registrations
- Trial days shown in sidebar
- All premium features available during trial
- After trial, FREE features only (unless upgraded)

## Troubleshooting

### Payment Not Processing
- Check database connection
- Verify Payment model exists
- Check terminal for Flask errors
- Ensure payment blueprint registered

### Bill Not Generating
- Verify user has electricity_provider set
- Check RR number is not empty
- Ensure consumption data exists
- Check utils/bill_generator.py imports

### PDF Download Issues
- Verify ReportLab installed: `pip install reportlab`
- Check file permissions in /tmp or temp directory
- Ensure send_file import in dashboard/routes.py

## Next Steps for Production

1. **Real Payment Integration**
   - Replace dummy payment with real Razorpay API
   - Add webhook handlers for payment confirmation
   - Implement refund logic

2. **Real Provider API**
   - Integrate with actual electricity provider APIs
   - Real-time RR number validation
   - Fetch actual tariff structures

3. **Email Configuration**
   - Set up SMTP server (Gmail/SendGrid)
   - Enable payment confirmation emails
   - Send bill via email

4. **Security Enhancements**
   - Add CSRF protection
   - Implement rate limiting
   - Secure payment data encryption

## Admin Credentials
- **Email**: admin@example.com
- **Password**: replace-with-strong-password

## Demo User Creation
Can create test users with different scenarios:
- Free user (no payments)
- Premium Monthly user (â‚¹99 payment)
- Premium Yearly user (â‚¹999 payment)
- User in trial period

---

**Status**: âœ… ALL FEATURES COMPLETE AND TESTED
**Version**: 1.0
**Date**: 2025

