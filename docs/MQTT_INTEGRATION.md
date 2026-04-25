# MQTT Real-Time Data Integration

## Overview

This guide explains how to integrate real-time hardware sensor data into EnergyTrack using MQTT protocol. The current application uses simulated data; this document shows how to transition to live hardware readings.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   ESP32 (Hardware)                      │
│         Reads: Voltage, Current, Power Consumption     │
└────────────┬────────────────────────────────────────────┘
             │
      [MQTT Publisher]
             │
     [MQTT Broker]  ← (e.g., Mosquitto, EMQX, HiveMQ)
             │
     [MQTT Subscriber]
             │
┌────────────▼────────────────────────────────────────────┐
│         Flask Backend (EnergyTrack Server)              │
│    - Subscribe to sensor topics                         │
│    - Store readings in database                         │
│    - Validate and process data                          │
└────────────┬────────────────────────────────────────────┘
             │
    [Existing Dashboard API]
             │
┌────────────▼────────────────────────────────────────────┐
│           Web Dashboard (React/HTML)                    │
│     - Real-time charts and alerts                       │
│     - Power usage by appliance                          │
│     - Billing preview                                   │
└─────────────────────────────────────────────────────────┘
```

## MQTT Topic Structure

Recommended topic hierarchy:

```
energytrack/
├── household/<household_id>/
│   ├── voltage
│   ├── current
│   ├── active_power
│   ├── energy_today
│   └── appliances/
│       ├── kitchen/power
│       ├── ac/power
│       └── water_heater/power
└── device/<device_id>/
    ├── status
    ├── last_update
    └── error_log
```

**Example MQTT Messages**:

```
Topic: energytrack/household/001/voltage
Payload: {"value": 230.5, "timestamp": "2026-04-25T10:30:45Z", "unit": "V"}

Topic: energytrack/household/001/current
Payload: {"value": 5.2, "timestamp": "2026-04-25T10:30:45Z", "unit": "A"}

Topic: energytrack/household/001/active_power
Payload: {"value": 1.15, "timestamp": "2026-04-25T10:30:45Z", "unit": "kW"}
```

## ESP32 Code Example

### Arduino Sketch (Pseudo-code)

```cpp
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// MQTT Broker
const char* mqtt_server = "192.168.x.x";  // Broker IP
int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

// Sensor pins
#define VOLTAGE_PIN 34
#define CURRENT_PIN 35
#define RELAY_PIN 23

// Calibration (adjust based on your sensors)
float voltage_multiplier = 230.0 / 1024.0;  // ADC to voltage
float current_multiplier = 20.0 / 1024.0;   // ADC to current

unsigned long last_publish = 0;
const unsigned long publish_interval = 5000;  // Publish every 5 seconds

void setup() {
  Serial.begin(115200);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  
  // Setup MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqtt_callback);
  
  // Setup pins
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
}

void loop() {
  // Reconnect if needed
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // Publish sensor data at intervals
  if (millis() - last_publish > publish_interval) {
    publish_sensor_data();
    last_publish = millis();
  }
}

void reconnect() {
  while (!client.connected()) {
    String clientId = "ESP32-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("MQTT connected");
      client.subscribe("energytrack/household/001/relay/+");
    } else {
      delay(5000);
    }
  }
}

void publish_sensor_data() {
  // Read ADC values
  int voltage_raw = analogRead(VOLTAGE_PIN);
  int current_raw = analogRead(CURRENT_PIN);
  
  // Convert to actual values (with voltage divider calibration)
  float voltage = voltage_raw * voltage_multiplier;
  float current = current_raw * current_multiplier;
  float power = voltage * current / 1000;  // kW
  
  // Create JSON payload
  String payload_v = "{\"value\": " + String(voltage, 2) + ", \"unit\": \"V\"}";
  String payload_i = "{\"value\": " + String(current, 2) + ", \"unit\": \"A\"}";
  String payload_p = "{\"value\": " + String(power, 3) + ", \"unit\": \"kW\"}";
  
  // Publish
  client.publish("energytrack/household/001/voltage", payload_v.c_str());
  client.publish("energytrack/household/001/current", payload_i.c_str());
  client.publish("energytrack/household/001/active_power", payload_p.c_str());
  
  Serial.printf("V: %.1f, I: %.2f, P: %.3f\n", voltage, current, power);
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  // Handle incoming relay commands
  String msg = "";
  for (int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  
  if (String(topic).indexOf("relay") > -1) {
    if (msg == "ON") {
      digitalWrite(RELAY_PIN, HIGH);
    } else if (msg == "OFF") {
      digitalWrite(RELAY_PIN, LOW);
    }
  }
}
```

---

## Flask Backend Integration

### 1. Install MQTT Client

```bash
pip install paho-mqtt
```

### 2. Create MQTT Service Module

**File**: `services/mqtt_handler.py`

```python
import paho.mqtt.client as mqtt
import json
from datetime import datetime
from models.database import db, ConsumptionLog, Device

class MQTTHandler:
    def __init__(self, broker_address, broker_port=1883):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT: Connected to broker")
            # Subscribe to all household topics
            client.subscribe("energytrack/household/+/voltage")
            client.subscribe("energytrack/household/+/current")
            client.subscribe("energytrack/household/+/active_power")
        else:
            print(f"MQTT: Connection failed with code {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            topic_parts = msg.topic.split("/")
            household_id = topic_parts[2]
            sensor_type = topic_parts[3]
            
            # Parse payload
            payload = json.loads(msg.payload.decode())
            value = payload.get("value")
            timestamp = payload.get("timestamp", datetime.now().isoformat())
            
            # Store in database
            self.store_sensor_reading(household_id, sensor_type, value, timestamp)
            print(f"MQTT: Stored {sensor_type} = {value} for household {household_id}")
        
        except Exception as e:
            print(f"MQTT: Error processing message: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"MQTT: Unexpected disconnection with code {rc}")
    
    def store_sensor_reading(self, household_id, sensor_type, value, timestamp):
        """Store sensor reading in database"""
        try:
            # Map to existing ConsumptionLog fields
            if sensor_type == "voltage":
                log = ConsumptionLog(
                    user_id=household_id,
                    timestamp=datetime.fromisoformat(timestamp),
                    voltage=value
                )
            elif sensor_type == "current":
                # Update existing log or create new
                log = ConsumptionLog.query.filter_by(
                    user_id=household_id,
                    timestamp=datetime.fromisoformat(timestamp)
                ).first()
                if log:
                    log.current = value
                else:
                    log = ConsumptionLog(
                        user_id=household_id,
                        timestamp=datetime.fromisoformat(timestamp),
                        current=value
                    )
            elif sensor_type == "active_power":
                log = ConsumptionLog(
                    user_id=household_id,
                    timestamp=datetime.fromisoformat(timestamp),
                    global_active_power=value
                )
            
            db.session.add(log)
            db.session.commit()
        
        except Exception as e:
            print(f"Database error: {e}")
    
    def start(self):
        """Start MQTT client"""
        self.client.connect(self.broker_address, self.broker_port, keepalive=60)
        self.client.loop_start()
    
    def stop(self):
        """Stop MQTT client"""
        self.client.loop_stop()
        self.client.disconnect()
```

### 3. Integrate into Flask App

**File**: `app.py` (modify)

```python
from services.mqtt_handler import MQTTHandler

# Initialize MQTT handler
mqtt_handler = MQTTHandler(broker_address="192.168.x.x", broker_port=1883)

@app.before_first_request
def startup():
    mqtt_handler.start()

@app.teardown_appcontext
def shutdown(exception=None):
    mqtt_handler.stop()

if __name__ == '__main__':
    app.run(debug=False)
```

---

## Setup Instructions

### Step 1: Install MQTT Broker (Local or Cloud)

**Option A: Local Mosquitto (Recommended for testing)**
```bash
# Windows
choco install mosquitto

# Linux
sudo apt-get install mosquitto mosquitto-clients

# Start broker
mosquitto -v
```

**Option B: Cloud MQTT Broker**
- HiveMQ Cloud (free tier): https://www.hivemq.com/mqtt-cloud/
- Use your credentials in ESP32 and Flask code

### Step 2: Configure Network

1. Ensure ESP32 and Flask server are on same WiFi network
2. Get broker IP address:
   ```bash
   ipconfig  # Windows
   ifconfig  # Linux
   ```
3. Update `mqtt_server` in ESP32 code
4. Update `broker_address` in Flask code

### Step 3: Deploy

1. Upload code to ESP32 via Arduino IDE
2. Start Flask app with MQTT handler
3. Monitor MQTT traffic (optional):
   ```bash
   mosquitto_sub -h 192.168.x.x -t "energytrack/#"
   ```

### Step 4: Verify Dashboard

- Open web dashboard at http://localhost:5000
- Check if real-time values appear instead of simulated data
- Verify `/api/live-data` endpoint returns actual sensor readings

---

## Transition from Simulated to Real Data

**Current behavior** (simulated):
- Dashboard API reads from `dataset.csv`
- Values loop through pre-generated consumption patterns

**New behavior** (real hardware):
- MQTT broker receives live ESP32 readings
- Flask stores in database
- Dashboard API queries latest database records
- No changes needed to frontend; data seamlessly switches

**Code change** (minimal):
```python
# Old: dashboard/routes.py
data = get_next_data_point()  # From CSV

# New: dashboard/routes.py
# Query latest from database (MQTT updated)
latest_log = ConsumptionLog.query.filter_by(
    user_id=current_user.id
).order_by(ConsumptionLog.timestamp.desc()).first()
```

---

## Troubleshooting MQTT

| Issue | Solution |
|-------|----------|
| ESP32 can't connect to broker | Check WiFi SSID/password; check broker IP and port; check firewall |
| Flask not receiving messages | Check subscription topics; verify MQTT broker is running; test with `mosquitto_sub` |
| Database not updating | Check database connection; verify topic parsing logic; check user_id mapping |
| Frequent disconnects | Reduce publish frequency; check WiFi signal; increase keepalive timeout |

---

## Performance Notes

- **Publish interval**: 5-10 seconds (balance between responsiveness and bandwidth)
- **Database storage**: Consider archiving old logs to prevent bloat
- **Dashboard refresh**: WebSocket real-time updates recommended for < 1 sec latency

---

**Version**: 1.0  
**Last Updated**: April 2026  
**Status**: Production-ready reference
