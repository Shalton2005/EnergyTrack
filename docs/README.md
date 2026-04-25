# Documentation

This folder contains comprehensive guides for implementing EnergyTrack with real-time hardware integration.

## Contents

### 1. [HARDWARE_ARCHITECTURE.md](HARDWARE_ARCHITECTURE.md)
**Overview of the complete system design**

- System block diagram
- Component list and specifications
- Power, sensing, and control sections
- Safety features and data flow
- Operating specifications
- Safety disclaimers

**Read this first** to understand the overall architecture and components involved.

---

### 2. [WIRING_GUIDE.md](WIRING_GUIDE.md)
**Step-by-step connection instructions**

- AC mains input and protection
- Power supply (HLK-PM01) connections
- Voltage sensor (ZMPT101B) wiring
- Current sensor (ACS712) with voltage divider
- Relay module connections
- ESP32 pinout and connections
- Common ground reference
- Testing checklist
- Voltage divider calculations
- Troubleshooting guide

**Follow this guide** when physically assembling the hardware circuit.

---

### 3. [MQTT_INTEGRATION.md](MQTT_INTEGRATION.md)
**Real-time data integration into Flask backend**

- MQTT architecture and data flow
- Topic structure and payload format
- ESP32 Arduino code example
- Flask MQTT handler implementation
- Backend integration steps
- MQTT broker setup
- Transitioning from simulated to real data
- Performance notes and troubleshooting

**Use this guide** to integrate live hardware readings into the web dashboard.

---

## Quick Start

### For Hardware Assembly:
1. Read [HARDWARE_ARCHITECTURE.md](HARDWARE_ARCHITECTURE.md) for overview
2. Follow [WIRING_GUIDE.md](WIRING_GUIDE.md) step-by-step
3. Test connections with multimeter before powering on

### For Software Integration:
1. Understand MQTT flow from [MQTT_INTEGRATION.md](MQTT_INTEGRATION.md)
2. Set up MQTT broker (local or cloud)
3. Upload ESP32 code with your WiFi credentials
4. Integrate Flask MQTT handler into application
5. Transition dashboard from simulated to real data

---

## Current State

**EnergyTrack v1.0.0 Status**:
- ✅ Web application with simulated data
- ✅ User and admin dashboards
- ✅ Billing and ML features
- 📋 Hardware integration (reference documentation)
- 📋 Real-time MQTT data (ready to implement)

To use real hardware:
1. Assemble circuit per wiring guide
2. Configure MQTT integration per integration guide
3. Dashboard will automatically display real-time readings

---

## Safety Disclaimer

⚠️ **High Voltage Hazard**

These guides cover work with 230V AC mains electricity. 

**Do not attempt without proper training.** All high-voltage work should be reviewed and approved by a qualified electrician before deployment to avoid:
- Electrical shock
- Fire hazard
- Equipment damage
- Personal injury

Follow all safety procedures in [WIRING_GUIDE.md](WIRING_GUIDE.md) before powering on.

---

## Component Trademarks

All component names, logos, and datasheets are property of their respective manufacturers:
- ESP32 © Espressif Systems
- ZMPT101B © Zhimeng Electronics
- ACS712 © Allegro Microsystems
- Hi-Link © Shenzhen Hi-Link Electronics
- Other components © respective owners

---

## Reference Images

Your circuit diagrams from Cirkit Designer are reference materials for:
- Component layout understanding
- Wiring path visualization
- Safety feature placement (MOV, fuse, terminals)

These are for **educational and prototype purposes only**.

---

## Questions or Issues?

Refer to troubleshooting sections in each guide:
- Hardware issues → [WIRING_GUIDE.md#troubleshooting](WIRING_GUIDE.md#troubleshooting)
- MQTT issues → [MQTT_INTEGRATION.md#troubleshooting-mqtt](MQTT_INTEGRATION.md#troubleshooting-mqtt)
- Architecture questions → [HARDWARE_ARCHITECTURE.md](HARDWARE_ARCHITECTURE.md)

---

**Documentation Version**: 1.0  
**Created**: April 2026  
**Project**: EnergyTrack - Household Energy Monitoring System
