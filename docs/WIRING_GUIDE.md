# Hardware Wiring Guide

## Step-by-Step Connection Instructions

### 1. AC Mains Input & Protection

**Components**: Fuse, MOV, Terminal Block, AC Cable

```
[Mains Cable] → [Terminal Block]
                     ↓
                [Phase (L)]  ──→ [Fuse (5-10A)] ──→ Relay COM / HLK input
                [Neutral (N)] ──→ Direct to HLK input & Load Neutral
```

**Procedure**:
1. Cut and strip AC mains cable (Phase, Neutral, Earth if available)
2. Insert Phase and Neutral into 2-pin terminal block
3. From terminal block:
   - Phase → 5-10A Fuse → Relay COM terminal
   - Neutral → HLK-PM01 AC input (N terminal)
4. **MOV Placement** (Critical):
   - Connect MOV across Phase and Neutral (parallel clamp)
   - Place after fuse, before load path
   - MOV protects all downstream components from voltage spikes

---

### 2. Power Supply: HLK-PM01 Module

**Connections**:
```
HLK-PM01 Input:
  - AC L (Phase) ← From Fuse
  - AC N (Neutral) ← From Mains

HLK-PM01 Output:
  - VCC (5V) → ESP32 VIN
  - VCC (5V) → Relay Module VCC
  - GND → Common Ground (all low-voltage devices)
```

**Wiring**:
1. Connect Phase (after fuse) to HLK AC L terminal
2. Connect Neutral to HLK AC N terminal
3. Connect HLK 5V output to:
   - ESP32 VIN pin
   - Relay module VCC pin
4. Connect HLK GND to common ground node

---

### 3. Voltage Sensor: ZMPT101B

**Connections**:
```
AC Measurement Point (Parallel to load):
  - One wire → ZMPT101B input pin
  - Other wire → ZMPT101B input pin

ZMPT101B Low-Voltage Side:
  - VCC → 5V (from HLK)
  - GND → Common Ground
  - OUT → (See voltage divider section below)
```

**Procedure**:
1. Identify AC line where you want to measure voltage
2. Connect one wire from AC line to ZMPT101B input (both terminals of sensor)
3. ZMPT101B output must be scaled before connecting to ESP32:
   - If your module already outputs 0-3.3V, connect OUT directly to GPIO34
   - If it outputs 0-5V, use voltage divider:

**Voltage Divider (if needed)**:
```
ZMPT101B OUT ──┬──→ [20kΩ resistor] ──→ [GPIO34]
               │
            [10kΩ resistor]
               │
             GND
```

Connect GPIO34 to the node between the two resistors.

---

### 4. Current Sensor: ACS712

**Connections**:
```
AC Current Path (Series):
  [Relay NO] → [ACS712 IN+] → [Load Phase]
               [ACS712 IN-] ← Connected in series
```

**Low-Voltage Side**:
```
ACS712 pins:
  - VCC → 5V (from HLK)
  - GND → Common Ground
  - OUT → Voltage Divider → GPIO35
```

**Procedure**:
1. Break the phase line going to load
2. Insert ACS712 in series:
   - Phase from relay NO → ACS712 IN+ terminal
   - ACS712 IN- terminal → Load phase wire
3. Connect VCC to 5V, GND to common ground
4. **Important**: ACS712 output must be scaled (always):

**Voltage Divider (Required)**:
```
ACS712 OUT ──┬──→ [20kΩ resistor] ──→ [GPIO35]
             │
          [10kΩ resistor]
             │
           GND
```

This scales 0-5V output to safe 0-3.3V for ESP32 ADC.

---

### 5. Relay Module: 4-Channel

**Connections**:
```
Relay Module Power:
  - VCC → 5V (from HLK)
  - GND → Common Ground

Relay Module Logic Inputs (to ESP32):
  - IN1 → GPIO23
  - IN2 → GPIO22
  - IN3 → GPIO21
  - IN4 → GPIO19

Relay Switching (for Load Control):
  - COM (Common) ← Relay NO connects to load
  - NO (Normally Open) ← Load phase wire
  - NC (Normally Closed) ← Not used (optional)
```

**Procedure**:
1. Power relay module with 5V and GND
2. Connect GPIO pins from ESP32 to relay IN1-IN4
3. For load switching:
   - Mains phase (after fuse) → Relay COM
   - Relay NO → Load phase wire
   - Neutral → Direct to load (not switched)

---

### 6. ESP32 Microcontroller

**Power**:
```
- VIN ← 5V from HLK-PM01
- GND ← Common Ground (all devices)
```

**Analog Inputs** (Sensor Readings):
```
- GPIO34 ← Voltage sensor OUT (through divider)
- GPIO35 ← Current sensor OUT (through divider)
```

**Digital Outputs** (Relay Control):
```
- GPIO23 ← Relay IN1
- GPIO22 ← Relay IN2
- GPIO21 ← Relay IN3
- GPIO19 ← Relay IN4
```

**Communication** (MQTT):
- TX/RX pins configured in code for MQTT broker connection

---

## Common Ground Reference

⚠️ **Critical Step**: All low-voltage components must share a common ground:

```
ESP32 GND ─┬─→ ZMPT101B GND
           ├─→ ACS712 GND
           ├─→ Relay Module GND
           └─→ HLK-PM01 GND (isolated from mains)
```

Use a ground bus (copper strip or terminal block) to connect all GND wires to one point.

---

## Testing Checklist

Before powering on:

- [ ] Fuse installed and accessible
- [ ] MOV connected across Phase-Neutral (parallel)
- [ ] All AC connections properly insulated
- [ ] Voltage dividers correctly wired
- [ ] Common ground connected for all low-voltage devices
- [ ] ESP32 powered by HLK-PM01 only (5V input)
- [ ] Relay module connected but load NOT yet connected
- [ ] All wire gauges appropriate for current (minimum 1.5mm² for mains)
- [ ] Enclosure complete and grounded
- [ ] No exposed mains conductors

---

## Voltage Divider Calculation

For safe ADC readings at 3.3V max:

**Formula**: V_out = V_in × (R2 / (R1 + R2))

For 5V input to 3.3V output:
- R1 = 20kΩ, R2 = 10kΩ
- V_out = 5V × (10k / 30k) = 1.67V (safe mid-range)
- At 0V input: 0V output
- At 5V input: 1.67V output (safe limit)

Adjust resistor values if needed based on sensor characteristics.

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| ESP32 not powering on | HLK-PM01 not connected properly | Check AC mains connection to HLK |
| Sensors reading 0 or max | Divider not connected | Verify voltage divider resistors |
| Relay clicks but load doesn't switch | GPIO not connected | Check GPIO-to-IN wiring |
| Frequent resets | Unstable 5V supply | Check HLK load capacity |
| No MQTT data | Code issue or broker | Verify WiFi and MQTT credentials |

---

## Safety Reminders

⚠️ **High Voltage Hazard**

- Do not work on live circuits
- Always disconnect mains before modifications
- Wear safety equipment (gloves, insulated tools)
- Have a qualified electrician review your setup
- Test with a multimeter before connecting load

---

**Reference Design**: EnergyTrack Hardware Module  
**Created**: April 2026  
**Status**: Prototype / Educational Reference
