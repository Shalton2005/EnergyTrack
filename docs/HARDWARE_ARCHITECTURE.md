# Hardware Architecture Reference

This document describes the reference hardware architecture for EnergyTrack real-time household energy monitoring.

## Overview

The EnergyTrack hardware system enables real-time measurement of electricity consumption in a household. It monitors voltage, current, and power usage across multiple appliances via a relay-controlled system, transmitting data to the Flask web application via MQTT protocol.

## System Block Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     AC MAINS (230V, 50Hz)                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    [Fuse]               [MOV Protection]
        │                     │
        └──────────┬──────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
[Voltage      [Current         [Relay
 Sensor]       Sensor]         Module]
     │             │             │
     └─────────────┴─────────────┤
                   │             │
              [ESP32 MCU]         │
              (Controller)        │
                   │             │
                   └─────────────┘
                         │
                    [To MQTT Broker]
                         │
                    [Flask Server]
                         │
                    [Web Dashboard]
```

## Components

| Component | Model | Purpose | Notes |
|-----------|-------|---------|-------|
| **Microcontroller** | ESP32 | Main control unit | ADC inputs for sensors, GPIO for relay control |
| **AC-DC Converter** | Hi-Link HLK-PM01 | 230V AC → 5V DC | Isolated power supply for ESP32 |
| **Voltage Sensor** | ZMPT101B | Measures AC voltage | Outputs 0-3.3V safe for ADC |
| **Current Sensor** | ACS712-5A/20A | Measures AC current | Requires voltage divider for safe ADC levels |
| **Relay Module** | 4-Channel 5V | Load switching | Controls appliances via GPIO |
| **Protection** | MOV + Fuse | Surge & overcurrent | MOV: Phase-Neutral parallel; Fuse: Series on phase |

## System Architecture

### Power Section
- **Input**: 230V AC, 50Hz (Indian mains)
- **Fuse**: 5-10A MCB or fuse cartridge (main protection)
- **MOV**: 250V Metal Oxide Varistor (surge protection, parallel across L-N)
- **HLK-PM01**: Isolated AC-DC converter outputs 5V DC @ ~0.6A
- **Output**: Powers ESP32 VIN and relay coils

### Sensing Section
- **Voltage Sensor (ZMPT101B)**:
  - Connected in parallel to AC line (measurement points)
  - Outputs 0-5V with 1.65V @ 0V
  - Must be scaled to 0-3.3V for safe ESP32 ADC
  
- **Current Sensor (ACS712)**:
  - Connected in series with phase line
  - Output: 2.5V ± (I × sensitivity)
  - For ACS712-5A: 0.185V per Amp
  - Maximum output can reach 5V; requires voltage divider

### Control Section
- **ESP32 GPIO Pins**:
  - GPIO34, GPIO35: Analog inputs for sensors
  - GPIO23, GPIO22, GPIO21, GPIO19: Digital outputs for relay control
  - Serial/MQTT: Communication to Flask server

- **Relay Module**:
  - Common (COM): Mains phase input
  - Normally Open (NO): Load phase output
  - Coil powered by 5V from HLK-PM01
  - Logic inputs from ESP32 GPIOs

## Key Safety Features

1. **Isolation**: HLK-PM01 provides isolation between mains and low-voltage circuit
2. **Surge Protection**: MOV clamps overvoltage spikes
3. **Overcurrent Protection**: Fuse/MCB limits current
4. **Sensor Safety**: Voltage divider/scaling ensures ADC inputs never exceed 3.3V
5. **Enclosure**: All components must be in an insulated enclosure
6. **Grounding**: Common low-voltage ground; isolated from mains ground

## Data Flow

```
Household AC Line
      ↓
[Sensors read V & I]
      ↓
[ESP32 processes readings]
      ↓
[MQTT publish to broker]
      ↓
[Flask Flask subscribes and stores]
      ↓
[Web dashboard displays real-time data]
```

## Operating Specifications

- **Input Voltage**: 180-264V AC (nominal 230V)
- **Frequency**: 50-60 Hz
- **Max Load**: Depends on relay rating (typically up to 16A @ 230V)
- **Sampling Rate**: Configurable (typical: 1-2 readings/sec)
- **Data Transmission**: MQTT @ 5-10 sec intervals
- **Operating Temperature**: 0-50°C (inside enclosure)

## Disclaimer

⚠️ **High-voltage work involves electrical hazard.** This reference architecture is for educational and prototype purposes only.

- Do NOT attempt assembly without proper electrical training.
- All wiring should be reviewed by a qualified electrician before deployment.
- Ensure proper enclosure, strain relief, and isolation.
- Use appropriate wire gauges and terminal blocks for current handling.
- Test all connections before connecting to mains.

---

**Created by**: Shalton2005  
**Hardware design tool**: Cirkit Designer  
**License**: Reference architecture; component trademarks remain with respective owners.
