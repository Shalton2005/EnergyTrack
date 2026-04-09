# EnergyTrack Dashboard - How It Works

## 📊 Data Flow Explanation

### 1. **Dataset.csv Simulation**
The system simulates real-time energy data using `dataset.csv`:

**Location**: `dataset.csv` (root directory)
**Format**: CSV file with columns:
- `datetime`: Timestamp of reading
- `global_active_power`: Power consumption in kilowatts (kW)
- `voltage`: Voltage level in volts (V)
- `current`: Current in amperes (A)
- `sub_metering1`: Kitchen & Laundry consumption (Wh)
- `sub_metering2`: Water Heater & AC consumption (Wh)
- `sub_metering3`: Electric Heater & Washer consumption (Wh)

**How it works**:
1. System loads `dataset.csv` on startup
2. Every 5 seconds, it fetches the next row from the dataset
3. If dataset doesn't exist, generates random dummy data
4. Data cycles back to start when it reaches the end
5. Each reading is saved to the database (`ConsumptionLog` table)

---

### 2. **Live Statistics Calculations**

#### **Current Power (kW)**
- **Source**: `global_active_power` from current dataset row
- **Calculation**: Direct value from dataset
- **Display**: Shows instant power consumption in kilowatts
- **Example**: 0.592 kW = 592 watts currently being used

#### **Voltage (V)**
- **Source**: `voltage` from current dataset row
- **Calculation**: Direct value from dataset  
- **Normal Range**: 220V - 240V
- **Alerts**: Triggers warning if outside normal range
- **Example**: 234.9V = Current voltage supply

#### **Today's Usage (kWh)**
- **Source**: All consumption logs from today (midnight to now)
- **Calculation**: 
  ```
  Sum of all global_active_power readings ÷ 60
  ```
- **Why divide by 60**: Readings are per minute, need hourly average
- **Example**: If you have 60 readings of 1kW each = 1 kWh

#### **Monthly Estimate (kWh)**
- **Source**: Today's consumption + time-based projection
- **Calculation**:
  ```
  Step 1: Daily average = Today's kWh ÷ Hours passed today × 24
  Step 2: Monthly = Daily average × 30 days
  ```
- **Example**: 
  - 2 kWh used in 10 hours today
  - Daily avg = (2 ÷ 10) × 24 = 4.8 kWh/day
  - Monthly = 4.8 × 30 = 144 kWh

---

### 3. **Sub-Meter Readings**

Sub-meters track individual appliance groups in Watt-hours (Wh):

#### **Kitchen & Laundry (sub_metering1)**
- **Includes**: Dishwasher, oven, microwave, washing machine
- **Unit**: Watt-hours (Wh)
- **Source**: Direct from dataset `sub_metering1` column

#### **Water Heater & AC (sub_metering2)**
- **Includes**: Water heater, air conditioning units
- **Unit**: Watt-hours (Wh)
- **Source**: Direct from dataset `sub_metering2` column

#### **Electric Heater & Washer (sub_metering3)**
- **Includes**: Electric heaters, clothes dryer
- **Unit**: Watt-hours (Wh)
- **Source**: Direct from dataset `sub_metering3` column

**Purpose**: Helps identify which appliances consume most power

---

### 4. **Graphs Explained**

#### **Live Power Consumption** (Left Chart)
- **Type**: Line chart
- **X-Axis**: Time (last 24 data points ≈ last 2 hours)
- **Y-Axis**: Power in kilowatts (kW)
- **Update**: Every 5 seconds
- **Shows**: Real-time power usage trend
- **Now**: Shows hourly pattern (24 points)

#### **Voltage Monitor** (Right Chart)
- **Type**: Line chart
- **X-Axis**: Time (last 24 data points)
- **Y-Axis**: Voltage in volts (V)
- **Update**: Every 5 seconds
- **Shows**: Voltage stability/fluctuations
- **Normal**: Should stay between 220V-240V

#### **Daily Consumption** (Bottom Chart)
- **Type**: Bar chart
- **X-Axis**: Days of the week (last 7 days)
- **Y-Axis**: Total consumption in kWh
- **Shows**: Historical consumption pattern
- **Purpose**: Compare daily usage

---

### 5. **Alert System**

#### **How Alerts are Created**:

1. **Voltage Fluctuation Alert**
   - **Trigger**: Voltage < 220V OR > 240V
   - **Message**: "Voltage fluctuation detected: {value}V"
   - **Severity**: Warning (yellow)
   - **Purpose**: Protect appliances from voltage spikes

2. **Power Spike Alert**
   - **Trigger**: Sudden 2x increase in power consumption
   - **Calculation**: Current power > (Average of last 5 readings × 2)
   - **Minimum**: Only if power > 2.0 kW
   - **Message**: "Sudden power spike detected: {value} kW"
   - **Severity**: Danger (red)
   - **Purpose**: Detect unusual consumption

#### **Alert Display**:
- **✅ Navbar**: Bell icon shows unread alert count
- **✅ Dropdown**: Click bell to see recent alerts
- **❌ Removed**: Bottom alert section (was cluttered)
- **Database**: Stored in `Alert` table with user_id

#### **Alert Fields**:
- `user_id`: Which user the alert belongs to
- `alert_type`: 'voltage' or 'spike'
- `message`: Description of the alert
- `severity`: 'warning', 'danger', or 'info'
- `is_read`: False by default, true when dismissed
- `created_at`: When alert was created

---

### 6. **Data Refresh Cycle**

```
Every 5 Seconds:
1. Frontend calls /dashboard/api/live-data
2. Backend fetches next row from dataset.csv
3. Saves to database (ConsumptionLog table)
4. Checks for alert conditions
5. Calculates today's total and monthly estimate
6. Returns JSON with all data
7. Frontend updates all displays
8. Charts add new point (keep last 24)
```

---

### 7. **Database Tables**

#### **ConsumptionLog**
Stores every energy reading:
- `id`: Unique identifier
- `user_id`: Which user owns this data
- `timestamp`: When reading was taken
- `global_active_power`: Power in kW
- `voltage`: Voltage in V
- `current`: Current in A
- `sub_metering1/2/3`: Sub-meter readings
- **Purpose**: Historical data for charts and calculations

#### **Alert**
Stores all alerts:
- `id`: Unique identifier
- `user_id`: Who the alert is for
- `alert_type`: Type of alert
- `message`: Alert text
- `severity`: How serious
- `is_read`: Whether user saw it
- `created_at`: When it happened

---

### 8. **What Changed**

✅ **Alerts now in navbar** - Bell icon with count
✅ **Removed bottom alert section** - Cleaner UI
✅ **Graphs show hourly data** - 24 points instead of 20
✅ **Numerical display fixed** - Proper decimal formatting
✅ **Better calculations** - Monthly estimate more accurate

---

## 🎯 Summary

**Live Data Flow**: dataset.csv → Python backend → Database → JSON API → JavaScript frontend → Charts/Stats

**Key Numbers**:
- **Current Power**: Instant reading (kW)
- **Today's Usage**: Sum÷60 for kWh
- **Monthly**: Today's pattern × 30 days
- **Sub-meters**: Individual appliance groups (Wh)
- **Alerts**: Automatic detection in navbar

**Restart the app** to see all changes!
