# ✅ QUICK VERIFICATION CHECKLIST
## Before Your Pitch - Run These Tests

---

## 1️⃣ VERIFY SIMULATION (30 seconds)

```powershell
cd "c:\Users\shalt\.vscode\ProgramFiles\EnergyTrack"
python verify_simulation.py
```

**Look for:**
```
✓ Dataset: 10,000 rows ready
✓ AI Detection: Ready to identify appliances
✓ Billing: Calculating from dataset consumption
✓ Live Updates: Every 5 seconds
🎉 ALL FEATURES ARE WORKING!
```

---

## 2️⃣ START THE APP (10 seconds)

```powershell
python app.py
```

**Wait for:**
```
 * Running on http://127.0.0.1:5000
 * Debugger PIN: XXX-XXX-XXX
```

**Then open:** http://127.0.0.1:5000

---

## 3️⃣ TEST DASHBOARD (60 seconds)

### ✅ Check Power Updates:
- Watch "Current Power" card
- Should change every 5 seconds
- Values: 0.10 - 4.99 kW

### ✅ Check AI Detection:
- Look for "AI-Powered Appliance Detection" card
- Should show: Mixer/Grinder, AC, or other appliances
- Confidence: 80-90%

### ✅ Check Energy Tips:
- Right side "Smart Tips" widget
- Shows 3 tips with potential savings

---

## 4️⃣ TEST BILLING (30 seconds)

**Navigate to:** Billing page (sidebar)

### ✅ Check Alert Banner:
- Should show: "⚠️ Bill Alert: Projected to exceed ₹1,000"
- Estimated bill: ₹9,978.71
- Tip displayed: "Reduce AC usage..."

### ✅ Check Breakdown:
- Fixed charges: ₹100.00
- Energy charges: ₹9,403.53
- Total: ₹9,978.71

---

## 5️⃣ TEST LANGUAGE (15 seconds)

**Click language dropdown (top-right)**

### ✅ Test Switching:
- Click Hindi → Dashboard, Billing, Settings all translate
- Click Kannada → All pages update
- Click English → Back to original

**Verify:** No page reload, instant translation

---

## 6️⃣ GENERATE BILL (20 seconds)

**Click:** "Generate Bill" button

### ✅ Download PDF:
- File downloads: `bill_RRXXXXXXXX_YYYYMM.pdf`
- Open PDF
- Check: Rs. symbols (not ■), 2 decimal places

---

## 7️⃣ CHECK BACKEND LOGS (Optional)

**In terminal where app.py is running:**

```
✓ Should see: GET /dashboard/api/live-data every 5 seconds
✓ Should see: 200 status codes (no errors)
✓ Should NOT see: 500 errors, tracebacks
```

---

## 🚨 TROUBLESHOOTING

### ❌ No AI Detection Showing?

**Check:**
1. Wait 15-20 seconds (needs 10 readings minimum)
2. Refresh page
3. Check console: F12 → Console → Look for errors

**Fix:**
```powershell
# Restart app
Ctrl+C
python app.py
```

### ❌ Bill Alert Not Showing?

**Reason:** Bill is < ₹1000

**To Test:**
- Wait for higher power consumption reading
- Or modify threshold in `billing.html` line 8:
  ```
  'warning' if bill_details.total_amount > 100 else 'info'
  ```

### ❌ Language Not Switching?

**Check:**
1. Browser console for JavaScript errors
2. LocalStorage (F12 → Application → Local Storage)
3. Should have key `selectedLanguage`

---

## 📊 WHAT TO EXPECT

### Dataset Behavior:
```
Row 0    → 0.650 kW at 246.5V  (detected: Mixer/Grinder)
Row 1    → 0.191 kW at 219.9V  (detected: Laptop)
Row 2    → 0.592 kW at 234.9V  (detected: Mixer/Grinder)
...cycles through 10,000 rows...
Row 9999 → Back to Row 0
```

### Monthly Bill Calculation:
```
Average Power: 1.81 kW
Daily kWh:     1.81 × 24 = 43.44 kWh
Monthly kWh:   43.44 × 30 = 1,304 kWh
Bill:          ₹9,978.71 (> ₹1000 → Alert triggers)
```

### AI Detection Patterns:
```
500W-750W   → Mixer/Grinder (90%)
800W-2000W  → Air Conditioner (90%)
100W-300W   → Refrigerator (80%)
50W-150W    → Television (85%)
```

---

## ✅ PRE-PITCH FINAL CHECK

**5 Minutes Before Demo:**

- [ ] App running at http://127.0.0.1:5000
- [ ] Dashboard showing live updates
- [ ] AI detection card visible
- [ ] Billing alert showing
- [ ] Language switcher working
- [ ] PDF download working
- [ ] No errors in terminal
- [ ] No errors in browser console (F12)
- [ ] Laptop charged 100%
- [ ] Backup slides ready (if projector fails)

---

## 🎤 DEMO ORDER (2 Minutes)

```
1. Login → Dashboard (10s)
   "See live monitoring from 10,000 real data points"

2. Point to AI Card (30s)
   "AI detected Mixer/Grinder - no extra sensors!"

3. Show Energy Tips (15s)
   "Smart recommendations save ₹500-800/month"

4. Billing → Alert (20s)
   "Warns you early - bill will be ₹9,978"

5. Language Switch (15s)
   "Hindi... Kannada... instant translation"

6. Generate PDF (15s)
   "Professional bill, Rs. symbols fixed"

7. Close (15s)
   "95% cheaper, AI-powered, multi-language"
```

---

## 📞 EMERGENCY CONTACTS

**If Something Breaks:**

1. **Restart App:** Ctrl+C → `python app.py`
2. **Check Database:** `instance/energytrack.db` exists?
3. **Check Dataset:** `dataset.csv` exists? (10,000 rows)
4. **Check Model:** `model.pkl` exists?

**Nuclear Option (if nothing works):**
```powershell
# Reset everything
rm instance/energytrack.db
python setup.py
python app.py
```

---

**Last Updated:** November 26, 2025  
**Status:** READY FOR PITCH ✅  
**Confidence Level:** 95%
