# HoloMed Quick Reference Guide

## 🎯 Start Here

This guide provides quick commands for common HoloMed tasks. For detailed information, see the specific guide documents.

---

## 🚀 Installation

### 1. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Verify installation
python -c "import vtk; print(f'VTK {vtk.__version__} installed')"
```

### 2. Prepare DICOM Data
```bash
# Place DICOM files in data directory
mkdir -p data/scripts/hardware
# Copy your .dcm files here
```

### 3. Configure ESP32 (Optional)
- Upload `hardware/gesture_sensor.ino` to ESP32
- Update WiFi SSID/Password in sketch
- Update MQTT broker IP (if using MQTT)

---

## 📺 Display Modes

### Mode 1: Standard Single Window
**Use Case**: Initial testing, DICOM exploration
```bash
python scripts/main.py
```
- Single viewport
- Interactive mouse controls
- Default DICOM path: `data/scripts/hardware/`

### Mode 2: Holographic 4-Way (Pepper's Ghost)
**Use Case**: Acrylic pyramid display, 360° visualization
```bash
python scripts/main.py --holographic
```
- 4 synchronized viewports
- Quad layout (2×2 grid)
- Perfect for group viewing

### Mode 3: Gesture-Controlled Holographic
**Use Case**: Interactive hand gesture control
```bash
# MQTT (Wireless)
python scripts/main.py --holographic --gesture --mqtt-broker 192.168.1.10

# Serial (USB)
python scripts/main.py --holographic --gesture --serial-port COM3
```
- Real-time gesture response
- <50ms latency target

---

## 🎮 Gesture Commands Reference

Perform these hand gestures in front of APDS-9960 sensor:

| Gesture | Hand Motion | Model Effect |
|---------|------------|--------------|
| **UP** | Swipe upward | Rotate tip toward (pitch) |
| **DOWN** | Swipe downward | Rotate tip away |
| **LEFT** | Swipe left | Rotate left (pan) |
| **RIGHT** | Swipe right | Rotate right |
| **NEAR** | Move hand toward sensor | Zoom in (1.1×) |
| **FAR** | Move hand away from sensor | Zoom out (0.9÷) |

---

## 🎨 Rendering Options

### Volume Rendering (Default - Better Quality)
```bash
python scripts/main.py
```
- GPU-accelerated ray casting
- Medical imaging quality
- ~30-60 FPS on modern GPUs
- Better for internal structures

### Surface Rendering (Faster - Better Speed)
```bash
python scripts/main.py --surface
```
- Marching cubes algorithm
- ~200+ FPS
- Better for boundary visualization
- Lower quality but faster

---

## 🖥️ Layout Options (Holographic Mode)

```bash
# Quad layout (2×2 grid) - BEST for pyramid
python scripts/main.py --holographic --layout quad

# Horizontal (1×4 strip)
python scripts/main.py --holographic --layout horizontal

# Vertical (4×1 stack)
python scripts/main.py --holographic --layout vertical

# Single viewport (debug only)
python scripts/main.py --holographic --layout single
```

---

## 🧪 Running Examples

### VTK Visualization Examples
```bash
# Basic volume rendering
python scripts/vtk_example.py --example 1

# Surface rendering (marching cubes)
python scripts/vtk_example.py --example 2

# Gesture simulation (automatic rotations)
python scripts/vtk_example.py --example 3

# Medical imaging windowing
python scripts/vtk_example.py --example 4
```

### 4-Way Viewport Examples
```bash
# Quad layout with 4 views
python scripts/viewport_example.py --example 1

# Reference geometry (axes + bounding box)
python scripts/viewport_example.py --example 4

# Single viewport debug mode
python scripts/viewport_example.py --example 5
```

### Gesture Control Examples
```bash
# Simulated gestures (no hardware needed)
python scripts/gesture_example.py --example 1

# MQTT wireless listener
python scripts/gesture_example.py --example 2 --mqtt-broker 192.168.1.XX

# Serial/USB listener
python scripts/gesture_example.py --example 3 --serial-port COM3

# Gesture pattern detection
python scripts/gesture_example.py --example 4
```

---

## 🔧 Advanced Options

### Custom DICOM Path
```bash
python scripts/main.py --data-path /path/to/dicom/folder/
```

### MQTT Configuration (Wireless)
```bash
python scripts/main.py --holographic --gesture \
  --gesture-input mqtt \
  --mqtt-broker 192.168.1.10
```
- **Default Broker**: 192.168.1.10
- **Default Topic**: holomed/gesture
- **Default Port**: 1883

### Serial Configuration (USB)
```bash
# Specific port
python scripts/main.py --holographic --gesture \
  --gesture-input serial \
  --serial-port COM3

# Auto-detect port (first available)
python scripts/main.py --holographic --gesture \
  --gesture-input serial
```
- **Common Ports**: COM3, COM4 (Windows) | /dev/ttyUSB0 (Linux)
- **Baud Rate**: 115200

---

## 📊 Performance Tips

### For Maximum FPS (Gaming-Like Experience)
```bash
# Use surface rendering instead of volume
python scripts/main.py --surface --holographic

# Use single viewport for debugging
python scripts/main.py --holographic --layout single
```

### For Best Gesture Latency (<50ms)
1. Use **Serial (USB)** instead of MQTT
2. Keep ESP32 close to PC
3. Use surface rendering
4. Disable reference geometry if needed

### For Best Graphics Quality
1. Use **Volume Rendering** (default)
2. Use **GPU rendering** (NVIDIA/AMD preferred)
3. Keep resolution at default (1024×1024)

---

## 🐛 Troubleshooting

### No DICOM Files Found
```bash
# Check path has .dcm files
ls data/scripts/hardware/

# Specify correct path
python scripts/main.py --data-path /path/to/dicom/
```

### MQTT Connection Failed
```bash
# Verify broker is running
mosquitto_sub -h 192.168.1.10 -t "holomed/gesture"

# Check ESP32 is connected to WiFi
# Update IP in gesture_sensor.ino if needed
```

### Serial Port Not Found
```bash
# List available ports
python -m serial.list_ports

# Use correct port
python scripts/main.py --gesture --serial-port COM3
```

### Low FPS / Slow Rendering
1. Switch to surface rendering: `--surface`
2. Update GPU drivers
3. Check system resources (CPU, RAM, GPU)
4. Reduce viewport resolution

### Gestures Not Working
1. Verify ESP32 code is uploaded correctly
2. Check sensor is wired (SDA=21, SCL=22)
3. Move hand 5-30cm from sensor
4. Avoid direct sunlight on sensor

---

## 📚 Documentation Guide

| Document | Purpose | Read When |
|----------|---------|-----------|
| **IMPLEMENTATION_SUMMARY.md** | Architecture overview, file structure | First-time setup |
| **VTK_VISUALIZATION_GUIDE.md** | Volume/surface rendering details | Working with 3D models |
| **VIEWPORT_GENERATOR_GUIDE.md** | Pepper's Ghost pyramid explanation | Setting up display |
| **GESTURE_CONTROL_GUIDE.md** | Real-time gesture input | Adding hand control |
| This file (QUICK_REFERENCE) | Commands and quick tips | Day-to-day usage |

---

## 🎓 Learning Path

### Beginner (30 minutes)
1. Run: `python scripts/main.py`
2. Read: IMPLEMENTATION_SUMMARY.md
3. Try: Examples 1 from each category

### Intermediate (1-2 hours)
1. Run all examples: `python scripts/*_example.py --example 1-4`
2. Read: VTK_VISUALIZATION_GUIDE.md
3. Try: `--holographic` mode

### Advanced (2-4 hours)
1. Read: All guide documents
2. Try: `--holographic --gesture` modes
3. Modify: Gesture mappings in gesture_control.py

---

## 💾 Configuration Files

### Main Application (`main.py`)
- CLI argument parsing
- Mode selection (single, holographic, gesture)
- Component initialization

### Gesture Configuration (`gesture_control.py`)
Edit `GestureConfig` class:
```python
ROTATE_AMOUNT = 10.0       # Degrees per gesture
ZOOM_IN_FACTOR = 1.1       # Zoom multiplier
DEBOUNCE_MS = 100          # Min time between gestures
HISTORY_LENGTH = 10        # Gestures to remember
```

### Logging Configuration (`logging_config.py`)
```python
logger = get_logger(debug=True)  # Enable debug
logger.record_metric("fps", 45.2, "frames/sec")
logger.print_metrics_summary()
```

---

## 🚀 Common Workflows

### Workflow 1: DICOM Exploration
```bash
# 1. Try basic visualization
python scripts/main.py

# 2. Try surface rendering if slow
python scripts/main.py --surface

# 3. View 4 perspectives
python scripts/main.py --holographic --layout quad
```

### Workflow 2: Setting Up Gesture Control
```bash
# 1. Test with simulated gestures
python scripts/gesture_example.py --example 1

# 2. Test actual hardware
python scripts/gesture_example.py --example 3 --serial-port COM3

# 3. Integrate with holographic display
python scripts/main.py --holographic --gesture --serial-port COM3
```

### Workflow 3: Pepper's Ghost Display Setup
```bash
# 1. View single perspective
python scripts/main.py

# 2. View 4 perspectives for pyramid
python scripts/main.py --holographic --layout quad

# 3. Add gesture control
python scripts/main.py --holographic --gesture --mqtt-broker 192.168.1.10
```

---

## 📞 Quick Fixes Cheatsheet

| Problem | Quick Fix |
|---------|-----------|
| Slow? | Add `--surface` flag |
| No gesture? | Try `--serial-port COM3` |
| No DICOM? | Check `data/scripts/hardware/` folder |
| MQTT failed? | Check IP with `ipconfig` (Windows) / `ifconfig` (Linux) |
| VTK error? | Update drivers, check GPU memory |
| Serial error? | Run `python -m serial.list_ports` |

---

## 🔗 Useful Commands

### System Info
```bash
# Check GPU info
nvidia-smi              # NVIDIA
rocm-smi                # AMD
intel_gpu_top           # Intel

# Check available serial ports
python -m serial.list_ports

# Test MQTT broker
mosquitto_pub -h 192.168.1.10 -t "test" -m "hello"
mosquitto_sub -h 192.168.1.10 -t "holomed/gesture"
```

### Development
```bash
# Run with debug logging
python scripts/main.py --debug

# Profile performance
python -m cProfile -s cumtime scripts/main.py

# Check imports/dependencies
python -c "import vtk, pydicom, paho.mqtt; print('OK')"
```

---

## 📝 Notes & Tips

1. **DICOM Files**: Must be `.dcm` format
2. **MQTT Broker**: Can use Mosquitto, HiveMQ, or local broker
3. **GPS/Compass**: Not required (gesture sensor only)
4. **Graphics**: Works on Intel iGPU, but NVIDIA/AMD preferred
5. **Latency**: Gesture-to-display is ~50ms (target met)

---

## 🆘 Getting Help

1. Check troubleshooting sections in specific guides
2. Review example code (`*_example.py`)
3. Check logging output (`./logs/` directory)
4. Review docstrings in source code

---

**Last Updated**: February 13, 2026  
**Version**: 1.0 (Complete Implementation)
