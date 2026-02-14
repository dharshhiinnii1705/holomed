"""
Gesture Control Integration Guide
Complete documentation for real-time hand gesture input system

======================================================================
OVERVIEW
======================================================================

The gesture control system bridges ESP32 sensor input (via MQTT or Serial)
with the VTK visualization system, enabling real-time interactive control
of the 3D holographic model.

Data Flow:
┌─────────────────────────────────────────────────────────────────┐
│  ESP32 + APDS-9960 Sensor  (gesture detection)                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Transmission: MQTT or Serial/USB                              │
│  Protocol: Wireless or Wired                                   │
│  Latency: < 50ms required                                      │
├─────────────────────────────────────────────────────────────────┤
│  GestureListenerThread  (background input receiver)            │
│  GestureHandler         (gesture-to-transformation mapper)     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  FourWayViewportGenerator (applies transformations)            │
│  VTK Render Window (displays updated 3D model)                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

======================================================================
GESTURE TYPES AND MAPPINGS
======================================================================

APDS-9960 Gesture Sensor provides 6 basic gestures:

┌────────┬─────────────────────┬─────────────────┬──────────────────┐
│Gesture │ How to Perform       │ Transformation  │ Visual Result    │
├────────┬─────────────────────┬─────────────────┬──────────────────┤
│ UP     │ Swipe hand UP       │ rotate(+10°, 0, 0)  │ Tip toward viewer│
│ DOWN   │ Swipe hand DOWN     │ rotate(-10°, 0, 0)  │ Tip away         │
│ LEFT   │ Swipe hand LEFT     │ rotate(0, +10°, 0)  │ Rotate left      │
│ RIGHT  │ Swipe hand RIGHT    │ rotate(0, -10°, 0)  │ Rotate right     │
│ NEAR   │ Move hand TOWARD    │ scale(1.1, 1.1, 1.1)│ Zoom in (magnify)│
│ FAR    │ Move hand AWAY      │ scale(0.9, 0.9, 0.9)│ Zoom out (shrink)│
└────────┴─────────────────────┴─────────────────┴──────────────────┘

Configuration in gesture_control.py (GestureConfig class):
  ROTATE_AMOUNT = 10.0          # Degrees per gesture
  ZOOM_IN_FACTOR = 1.1          # Scale factor for zoom in
  ZOOM_OUT_FACTOR = 1.0/1.1     # Scale factor for zoom out
  DEBOUNCE_MS = 100             # Minimum time between gestures
  HISTORY_LENGTH = 10           # Gestures to remember

======================================================================
ARCHITECTURE COMPONENTS
======================================================================

1. GestureHandler
   ─────────────────────────────────────────────────────────────────
   Responsibilities:
   - Maps gesture input to VTK transformations
   - Maintains gesture history for pattern detection
   - Handles debouncing (prevents rapid duplicate gestures)
   - Tracks statistics (total count, last gesture, history)
   - Detects multi-gesture sequences (swipes, combinations)
   
   Key Methods:
   - handle_gesture(gesture_str) → Processes a single gesture
   - detect_swipe() → Identifies motion patterns
   - _apply_transformation(gesture) → Applies VTK transform
   - get_statistics() → Returns gesture stats

2. GestureListenerThread
   ─────────────────────────────────────────────────────────────────
   Responsibilities:
   - Runs in background thread (non-blocking)
   - Connects to MQTT broker or serial port
   - Receives incoming gesture messages
   - Passes gestures to GestureHandler
   - Monitors connection and errors
   
   Input Modes:
   - "mqtt": Wireless from ESP32 (requires WiFi + MQTT broker)
   - "serial": Wired via USB serial (direct connection)
   
   Key Methods:
   - start() → Begin listening
   - stop() → Stop listening cleanly
   - _listen_mqtt() → MQTT connection loop
   - _listen_serial() → Serial connection loop

3. Integration with FourWayViewportGenerator
   ─────────────────────────────────────────────────────────────────
   When a gesture is received:
   1. GestureListenerThread receives "UP"
   2. GestureHandler.handle_gesture("UP") called
   3. _apply_transformation() calls viewport.rotate_all(10, 0, 0)
   4. ViewportGenerator synchronizes all 4 renderers
   5. viewport.render() refreshes display
   6. All 4 viewers see synchronized rotation

======================================================================
QUICK START - MQTT (WIRELESS)
======================================================================

Prerequisites:
1. MQTT broker running (e.g., Mosquitto on local network)
2. ESP32 connected to WiFi with gesture_sensor.ino uploaded
3. Python packages: pip install paho-mqtt

Code Example:
─────────────────────────────────────────────────────────────────────
from gesture_control import GestureHandler, GestureListenerThread
from viewport_generator import FourWayViewportGenerator
from vtk_visualizer import VTKVisualizer

# Setup visualization
viz = VTKVisualizer()
viz.create_volume_from_dicom(loader)

viewport = FourWayViewportGenerator()
viewport.add_volume(viz.volume_actor)

# Setup gesture control
handler = GestureHandler(viewport)
listener = GestureListenerThread(
    handler,
    input_mode="mqtt",
    mqtt_broker="192.168.1.10"  # Your MQTT broker IP
)

# Start listening and displaying
listener.start()
try:
    viewport.show()
finally:
    listener.stop()
─────────────────────────────────────────────────────────────────────

Run example:
  python gesture_example.py --example 2 --mqtt-broker 192.168.1.10

======================================================================
QUICK START - SERIAL (USB)
======================================================================

Prerequisites:
1. ESP32 connected to PC via USB cable
2. What port shows up (COM3, /dev/ttyUSB0, etc.)
3. Python packages: pip install pyserial

Code Example:
─────────────────────────────────────────────────────────────────────
from gesture_control import GestureHandler, GestureListenerThread
from viewport_generator import FourWayViewportGenerator

# Setup viewport
viewport = FourWayViewportGenerator()
# ... add volume ...

# Setup gesture control
handler = GestureHandler(viewport)
listener = GestureListenerThread(
    handler,
    input_mode="serial",
    serial_port="COM3"  # Or /dev/ttyUSB0 on Linux
)

# Auto-detect port (optional)
# listener = GestureListenerThread(
#     handler,
#     input_mode="serial"
# )

listener.start()
try:
    viewport.show()
finally:
    listener.stop()
─────────────────────────────────────────────────────────────────────

Run example:
  python gesture_example.py --example 3 --serial-port COM3

======================================================================
GESTURE PATTERN DETECTION
======================================================================

The system can detect multi-gesture sequences:

Example Patterns:
  "UP, UP, UP"          → Fast swipe upward
  "LEFT, LEFT, LEFT"    → Fast swipe left
  "UP, LEFT"            → Diagonal motion
  "UP, LEFT, UP"        → Complex motion

Detection Code:
─────────────────────────────────────────────────────────────────────
pattern = handler.detect_swipe()
if pattern == "Fast swipe UP":
    # Do something special
    viewport.rotate_all(30, 0, 0)  # Bigger rotation
    
# Gesture history shows last N gestures
stats = handler.get_statistics()
print(stats['recent_gestures'])  # ['UP', 'UP', 'LEFT', ...]
─────────────────────────────────────────────────────────────────────

======================================================================
REAL-TIME LATENCY OPTIMIZATION
======================================================================

Target: < 50ms gesture-to-display response time

Latency Budget:
  ESP32 gesture detection:     ~5ms
  WiFi/Serial transmission:    ~5-10ms
  Python processing:           ~5ms
  VTK rendering:              ~20-30ms
  Display refresh:             ~5-10ms
  ─────────────────────────────────────
  Total budget:                50ms

Optimization Tips:
1. Use serial (USB) instead of MQTT if possible (lower latency)
2. Keep gesture debounce low (currently 100ms - may be too high)
3. Use surface rendering instead of volume for faster frames
4. Ensure ESP32 WiFi signal is strong (< 1 bar latency)
5. Disable reference geometry (axes, bounding box) if needed
6. Run on dedicated GPU (not integrated graphics)

Latency Check:
─────────────────────────────────────────────────────────────────────
# Print statistics to see actual latency
handler.print_statistics()
listener.print_statistics()

# Example output:
# Gesture Statistics
# Total gestures: 45
# Messages received: 45
# Errors: 0
─────────────────────────────────────────────────────────────────────

======================================================================
CONFIGURATION CUSTOMIZATION
======================================================================

Edit gesture_control.py GestureConfig class to change behavior:

  ROTATE_AMOUNT = 5.0           # Smaller rotations per gesture
  ZOOM_IN_FACTOR = 1.2          # More aggressive zoom
  DEBOUNCE_MS = 50              # Faster response (careful: may skip)
  HISTORY_LENGTH = 5            # Remember fewer gestures

Example - Aggressive Control:
─────────────────────────────────────────────────────────────────────
class GestureConfig:
    ROTATE_AMOUNT = 15.0         # More rotation per gesture
    ZOOM_IN_FACTOR = 1.2         # Stronger zoom
    ZOOM_OUT_FACTOR = 1.0/1.2    # Match zoom out
    DEBOUNCE_MS = 50             # Faster
─────────────────────────────────────────────────────────────────────

======================================================================
ERROR HANDLING AND DEBUGGING
======================================================================

Common Issues:

1. MQTT Connection Failed
   - Check broker IP address is correct
   - Verify ESP32 can reach broker
   - Check firewall allows port 1883
   - Run: mosquitto_sub -h 192.168.1.10 -t "holomed/gesture"

2. Serial Connection Failed
   - Check device shows up: python -m serial.list_ports
   - Verify USB cable is properly connected
   - Check correct port (COM3, /dev/ttyUSB0, etc.)
   - Correct baud rate in gesture.ino: 115200

3. Gestures Not Triggering
   - Verify ESP32 code has MQTT_ENABLED or serial output enabled
   - Check gesture sensor is properly wired (SDA=GPIO21, SCL=GPIO22)
   - Move hand slowly for better detection (2-30cm distance)
   - Ensure hand not in direct sunlight (IR sensor)

4. Latency Issues
   - Time lag between gesture and model rotation
   - Solution: Lower DEBOUNCE_MS, use serial instead of MQTT
   - Switch to surface rendering (faster)

Debug Logging:
─────────────────────────────────────────────────────────────────────
# Print all gestures as received
for gesture in handler.gesture_history:
    print(gesture.value)

# Monitor listener status
while listener.running:
    stats = listener.get_statistics()
    print(f"Messages: {stats['messages_received']}, Errors: {stats['errors']}")
    time.sleep(1)
─────────────────────────────────────────────────────────────────────

======================================================================
ADVANCED - CUSTOM GESTURE MAPPINGS
======================================================================

To implement custom gesture mappings, modify GestureHandler:

─────────────────────────────────────────────────────────────────────
class GestureHandler:
    def _apply_transformation(self, gesture):
        if gesture == GestureType.UP:
            # Custom: Move in 3D space instead of rotate
            self.viewport_system.translate_all(0, 10, 0)
        elif gesture == GestureType.NEAR:
            # Custom: Raise the model instead of zoom
            self.viewport_system.translate_all(0, 0, 10)
─────────────────────────────────────────────────────────────────────

======================================================================
NEXT STEPS
======================================================================

1. [DONE] Gesture input handling (GestureHandler)
2. [DONE] Real-time listener (GestureListenerThread)
3. [IN PROGRESS] Integration with main.py for unified control
4. [TODO] Multi-gesture macros (hold + swipe combinations)
5. [TODO] Gesture recording/replay for demonstrations
6. [TODO] Gesture calibration for user preferences
7. [TODO] Machine learning for custom gesture recognition

======================================================================
"""

# This file is documentation only
