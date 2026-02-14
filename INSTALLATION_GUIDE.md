# 🔧 HoloMed Installation & Setup Guide

## Pre-Flight Check Results

Your system has been validated. Here's what we found:

✅ **Working**
- Python 3.13 (excellent!)
- Gesture control system ✓
- Logging system ✓
- Documentation ✓
- Example programs ✓

❌ **Missing (Critical)**
- VTK (3D visualization library) - **REQUIRED**
- pydicom (DICOM file handling) - **REQUIRED**
- matplotlib, scipy, pyserial - **REQUIRED**

⚠️ **Notes**
- RAM: 3.82 GB (limited but acceptable)
- DICOM files: Not found yet (add to `data/scripts/hardware/`)

---

## 🚀 Installation Steps

### Step 1: Install Python Dependencies

This is the **only** step needed before you can use HoloMed!

```bash
cd c:\Users\dhars\OneDrive\Desktop\HoloMed_Project
pip install -r requirements.txt
```

**What this installs:**
- VTK 9.0+ (3D graphics engine)
- pydicom (DICOM medical imaging)
- NumPy, SciPy (numerical computing)
- matplotlib (plotting)
- Pillow (image processing)
- pyserial (USB communication)
- paho-mqtt (wireless gesture input)

**Installation Time**: 5-15 minutes depending on internet speed

### Step 2: Verify Installation

Run the pre-flight check again to confirm everything works:

```bash
python scripts/pre_flight_check.py
```

You should see: **✅ ALL CRITICAL CHECKS PASSED**

---

## 📋 Installation Troubleshooting

### Issue: "pip" command not found

```bash
# Use python -m pip instead
python -m pip install -r requirements.txt

# Or specify full path
C:\Users\dhars\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\Scripts\pip.exe install -r requirements.txt
```

### Issue: Permission Denied on Windows

```bash
# Run as Administrator or use --user flag
pip install --user -r requirements.txt
```

### Issue: VTK Installation Takes Long Time

This is normal! VTK compiles from source on some systems.
- Installation can take 10-20 minutes
- This is a one-time process
- Be patient and let it complete

### Issue: specific package fails to install

Install packages individually to identify the problem:

```bash
pip install numpy
pip install matplotlib
pip install vtk
pip install pydicom
pip install scipy
pip install pyserial
pip install pillow
pip install paho-mqtt
```

---

## 🎯 Quick Start (After Installation)

### 1. Test Basic Visualization (No Hardware)
```bash
python scripts/main.py
```
- Opens an interactive 3D window
- Requires DICOM files in `data/scripts/hardware/`
- Use mouse to rotate/zoom

### 2. Run Examples
```bash
# Quick examples (gesture simulation, no hardware needed)
python scripts/vtk_example.py --example 1
python scripts/gesture_example.py --example 1
python scripts/viewport_example.py --example 1
```

### 3. Enable 4-Way Holographic Display
```bash
python scripts/main.py --holographic
```
Shows 4 synchronized views (for Pepper's Ghost pyramid)

### 4. Add Gesture Control (When Hardware Ready)
```bash
python scripts/main.py --holographic --gesture --serial-port COM3
```

---

## 📂 Adding DICOM Medical Images

Your DICOM files should go here:
```
HoloMed_Project/data/scripts/hardware/
```

**Steps:**
1. Create directory if it doesn't exist:
   ```bash
   mkdir data\scripts\hardware
   ```

2. Copy DICOM files (.dcm) to this folder

3. Run visualization:
   ```bash
   python scripts/main.py
   ```

**Common DICOM sources:**
- Medical imaging equipment (CT, MRI, etc.)
- DICOM test datasets from:
  - https://www.dicomstandard.org/
  - https://github.com/neurolabusc/dcm2niix/tree/master/sample
  - Your hospital/clinic PACS system

---

## 🔌 Hardware Setup (When Ready - Optional)

### ESP32 Gesture Sensor Setup

Prerequisites:
- ESP32 microcontroller
- APDS-9960 gesture sensor
- Arduino IDE installed

**Steps:**

1. **Connect Hardware:**
   - APDS-9960 SDA → GPIO21
   - APDS-9960 SCL → GPIO22
   - 5V → 5V, GND → GND

2. **Upload Firmware:**
   ```bash
   # Open Arduino IDE
   # Load: hardware/gesture_sensor.ino
   # Select: Board = ESP32, Port = COMx
   # Click Upload
   ```

3. **Find Serial Port:**
   ```bash
   python -m serial.list_ports
   ```
   Should show something like: `COM3`, `COM4`, etc.

4. **Test Connection:**
   ```bash
   python scripts/gesture_example.py --example 3 --serial-port COM3
   ```
   Make hand gestures in front of sensor!

5. **Integrate with Visualization:**
   ```bash
   python scripts/main.py --holographic --gesture --serial-port COM3
   ```

### MQTT Setup (Optional - For Wireless Gestures)

If you want wireless gesture control:

1. **Install MQTT Broker** (mosquitto):
   ```bash
   # Windows: Download mosquitto from https://mosquitto.org/download/
   # Or: choco install mosquitto  (if using Chocolatey)
   ```

2. **Update ESP32 Firmware:**
   Edit `hardware/gesture_sensor.ino`:
   ```cpp
   const char* WIFI_SSID = "YOUR_WIFI_SSID";
   const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";
   const char* MQTT_SERVER = "192.168.1.X";  // Your PC IP
   ```

3. **Find Your PC IP:**
   ```bash
   ipconfig
   # Look for "IPv4 Address" (usually 192.168.1.x)
   ```

4. **Test MQTT Connection:**
   ```bash
   python scripts/gesture_example.py --example 2 --mqtt-broker 192.168.1.X
   ```

5. **Enable Wireless Gestures:**
   ```bash
   python scripts/main.py --holographic --gesture --mqtt-broker 192.168.1.X
   ```

---

## ✅ Checklist

- [ ] Ran `pip install -r requirements.txt`
- [ ] Ran `python scripts/pre_flight_check.py` and saw all checks pass
- [ ] Can run `python scripts/main.py` (or examples)
- [ ] DICOM files added to `data/scripts/hardware/` (optional for visualization)
- [ ] Ready to connect hardware (optional)

---

## 📞 Support

If you encounter issues:

1. **Check logs:**
   ```bash
   # View latest log
   type logs\holomed_*.log
   ```

2. **Read troubleshooting:**
   - QUICK_REFERENCE.md
   - VTK_VISUALIZATION_GUIDE.md
   - GESTURE_CONTROL_GUIDE.md

3. **Run pre-flight check:**
   ```bash
   python scripts/pre_flight_check.py
   ```

---

## 🎓 Next: Learning Path

### Phase 1: Basic Setup (Now)
- [x] Install dependencies
- [x] Run pre-flight check
- Next: Add DICOM files (see above)

### Phase 2: Explore Software (30 min)
- Run basic visualization: `python scripts/main.py`
- Run examples: `python scripts/*_example.py --example 1`
- Read: QUICK_REFERENCE.md

### Phase 3: Holographic Display Setup (1 hour)
- Enable 4-way view: `--holographic`
- Understand Pepper's Ghost: Read VIEWPORT_GENERATOR_GUIDE.md
- Test layouts: `--layout quad` / `horizontal` / `vertical`

### Phase 4: Add Gesture Control (1-2 hours - Optional)
- Test gesture simulation first: `gesture_example.py --example 1`
- Connect ESP32 hardware (if available)
- Enable real-time gestures: `--gesture --serial-port COM3`
- Read: GESTURE_CONTROL_GUIDE.md

---

**Status**: Ready for software setup! 🎉

Next: `pip install -r requirements.txt` and you're good to go!
