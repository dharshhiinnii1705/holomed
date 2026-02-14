"""
Gesture Control Integration Module
Connects ESP32 gesture sensor input to VTK model transformations

This module bridges the gesture input (MQTT or Serial) with the
visualization system for real-time interactive control.

Features:
- Gesture event listener and dispatcher
- Gesture-to-transformation mapping
- Real-time model synchronization
- Multi-gesture sequences (hold/swipe combinations)
- Gesture history and debouncing
"""

import threading
import queue
import time
from enum import Enum
from collections import deque


class GestureType(Enum):
    """Enum for gesture types from ESP32 APDS-9960"""
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    NEAR = "NEAR"        # Hand moved toward sensor (pinch)
    FAR = "FAR"          # Hand moved away from sensor (spread)
    UNKNOWN = "UNKNOWN"


class GestureConfig:
    """Configuration for gesture-to-transformation mapping"""
    
    # Basic rotation parameters (degrees per gesture)
    ROTATE_AMOUNT = 10.0
    
    # Scale parameters (zoom factor)
    ZOOM_IN_FACTOR = 1.1
    ZOOM_OUT_FACTOR = 1.0 / 1.1
    
    # Translation parameters
    TRANSLATE_AMOUNT = 10.0
    
    # Debounce timing (milliseconds)
    DEBOUNCE_MS = 100
    
    # Gesture history length (for multi-gesture detection)
    HISTORY_LENGTH = 10


class GestureHandler:
    """
    Maps gestures to viewport transformations and handles real-time control
    
    Gesture Mappings:
    ─────────────────────────────────────────────────────────────────
    Gesture     →   Transformation           →   Visual Effect
    ─────────────────────────────────────────────────────────────────
    UP          →   rotate_all(+rx, 0, 0)   →   Rotate model up/toward
    DOWN        →   rotate_all(-rx, 0, 0)   →   Rotate model down/away
    LEFT        →   rotate_all(0, +ry, 0)   →   Rotate model left
    RIGHT       →   rotate_all(0, -ry, 0)   →   Rotate model right
    NEAR        →   scale_all(zoom_in...)   →   Zoom in / Magnify
    FAR         →   scale_all(zoom_out...)  →   Zoom out / Shrink
    ─────────────────────────────────────────────────────────────────
    """
    
    def __init__(self, viewport_system=None):
        """
        Initialize gesture handler
        
        Args:
            viewport_system: FourWayViewportGenerator instance
                           (can be set later with set_viewport_system)
        """
        self.viewport_system = viewport_system
        
        # Configuration
        self.config = GestureConfig()
        
        # Gesture history for multi-gesture detection
        self.gesture_history = deque(maxlen=self.config.HISTORY_LENGTH)
        
        # Last gesture timestamp (for debouncing)
        self.last_gesture_time = 0
        
        # Statistics
        self.gesture_count = 0
        self.last_gesture = None
    
    def set_viewport_system(self, viewport_system):
        """
        Set the viewport system to control
        
        Args:
            viewport_system: FourWayViewportGenerator instance
        """
        self.viewport_system = viewport_system
    
    def handle_gesture(self, gesture_str):
        """
        Handle a gesture event and apply transformation
        
        Args:
            gesture_str (str): Gesture as string ("UP", "DOWN", etc.)
            
        Returns:
            bool: True if gesture was processed, False if debounced
        """
        if self.viewport_system is None:
            print("⚠️ Warning: No viewport system set")
            return False
        
        # Debounce check
        current_time = time.time() * 1000  # Convert to milliseconds
        if current_time - self.last_gesture_time < self.config.DEBOUNCE_MS:
            return False
        
        self.last_gesture_time = current_time
        
        # Convert string to GestureType
        try:
            gesture = GestureType[gesture_str]
        except KeyError:
            gesture = GestureType.UNKNOWN
        
        # Add to history
        self.gesture_history.append(gesture)
        
        # Track stats
        self.gesture_count += 1
        self.last_gesture = gesture
        
        # Apply transformation based on gesture
        self._apply_transformation(gesture)
        
        # Render updated view
        self.viewport_system.render()
        
        return True
    
    def _apply_transformation(self, gesture):
        """
        Apply VTK transformation based on gesture
        
        Args:
            gesture (GestureType): The gesture to process
        """
        vp = self.viewport_system
        rotate = self.config.ROTATE_AMOUNT
        
        if gesture == GestureType.UP:
            # Rotate around X-axis (tip model toward viewer)
            vp.rotate_all(rotate, 0, 0)
            print(f"→ UP: Rotated +{rotate}° around X-axis")
            
        elif gesture == GestureType.DOWN:
            # Rotate around X-axis (tip model away)
            vp.rotate_all(-rotate, 0, 0)
            print(f"→ DOWN: Rotated -{rotate}° around X-axis")
            
        elif gesture == GestureType.LEFT:
            # Rotate around Y-axis (tip to left)
            vp.rotate_all(0, rotate, 0)
            print(f"→ LEFT: Rotated +{rotate}° around Y-axis")
            
        elif gesture == GestureType.RIGHT:
            # Rotate around Y-axis (tip to right)
            vp.rotate_all(0, -rotate, 0)
            print(f"→ RIGHT: Rotated -{rotate}° around Y-axis")
            
        elif gesture == GestureType.NEAR:
            # Scale up (zoom in)
            zoom = self.config.ZOOM_IN_FACTOR
            vp.scale_all(zoom, zoom, zoom)
            print(f"→ NEAR: Zoomed in ({zoom:.2f}×)")
            
        elif gesture == GestureType.FAR:
            # Scale down (zoom out)
            zoom = self.config.ZOOM_OUT_FACTOR
            vp.scale_all(zoom, zoom, zoom)
            print(f"→ FAR: Zoomed out ({zoom:.2f}×)")
            
        else:
            print(f"? UNKNOWN: No mapping for gesture")
    
    def detect_swipe(self):
        """
        Detect multi-gesture swipe patterns
        
        Example patterns:
        - UP, UP, UP = Fast swipe up
        - LEFT, RIGHT = Oscillation
        - UP, LEFT, UP = Diagonal motion
        
        Returns:
            str: Description of detected pattern, or None
        """
        if len(self.gesture_history) < 3:
            return None
        
        # Get last 3 gestures
        recent = list(self.gesture_history)[-3:]
        
        # Detect patterns
        if all(g == GestureType.UP for g in recent):
            return "Fast swipe UP"
        elif all(g == GestureType.DOWN for g in recent):
            return "Fast swipe DOWN"
        elif all(g == GestureType.LEFT for g in recent):
            return "Fast swipe LEFT"
        elif all(g == GestureType.RIGHT for g in recent):
            return "Fast swipe RIGHT"
        elif recent[0] == GestureType.UP and recent[1] == GestureType.LEFT:
            return "Diagonal UP-LEFT"
        elif recent[0] == GestureType.UP and recent[1] == GestureType.RIGHT:
            return "Diagonal UP-RIGHT"
        
        return None
    
    def reset_history(self):
        """Clear gesture history"""
        self.gesture_history.clear()
    
    def get_statistics(self):
        """
        Get gesture statistics
        
        Returns:
            dict: Statistics about gesture input
        """
        return {
            "total_gestures": self.gesture_count,
            "last_gesture": self.last_gesture.value if self.last_gesture else None,
            "history_length": len(self.gesture_history),
            "recent_gestures": [g.value for g in self.gesture_history],
        }
    
    def print_statistics(self):
        """Print gesture statistics to console"""
        stats = self.get_statistics()
        print("\n" + "="*50)
        print("Gesture Statistics")
        print("="*50)
        print(f"Total gestures: {stats['total_gestures']}")
        print(f"Last gesture: {stats['last_gesture']}")
        print(f"Recent (last {len(stats['recent_gestures'])}): {' → '.join(stats['recent_gestures'])}")
        print("="*50 + "\n")


class GestureListenerThread:
    """
    Background thread for listening to gesture input
    
    Supports both MQTT and Serial input modes
    """
    
    def __init__(self, gesture_handler, input_mode="mqtt", 
                 mqtt_broker="192.168.1.10", serial_port=None):
        """
        Initialize gesture listener thread
        
        Args:
            gesture_handler (GestureHandler): Handler for gestures
            input_mode (str): "mqtt" or "serial"
            mqtt_broker (str): MQTT broker address (if using MQTT)
            serial_port (str): Serial port (if using serial)
        """
        self.gesture_handler = gesture_handler
        self.input_mode = input_mode
        self.mqtt_broker = mqtt_broker
        self.serial_port = serial_port
        
        # Control
        self.running = False
        self.thread = None
        
        # Statistics
        self.messages_received = 0
        self.errors = 0
    
    def start(self):
        """Start listening for gestures"""
        if self.running:
            print("⚠️ Gesture listener already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        
        print(f"✓ Gesture listener started ({self.input_mode.upper()} mode)")
    
    def stop(self):
        """Stop listening"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print("✓ Gesture listener stopped")
    
    def _listen_loop(self):
        """Main listening loop (runs in background thread)"""
        try:
            if self.input_mode == "mqtt":
                self._listen_mqtt()
            elif self.input_mode == "serial":
                self._listen_serial()
            else:
                print(f"❌ Unknown input mode: {self.input_mode}")
        except Exception as e:
            print(f"❌ Error in gesture listener: {e}")
            self.errors += 1
    
    def _listen_mqtt(self):
        """Listen for gestures via MQTT"""
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            print("❌ paho-mqtt not installed. Install with: pip install paho-mqtt")
            return
        
        MQTT_TOPIC = "holomed/gesture"
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"✓ Connected to MQTT broker {self.mqtt_broker}")
                client.subscribe(MQTT_TOPIC)
            else:
                print(f"❌ MQTT connection failed (rc={rc})")
        
        def on_message(client, userdata, msg):
            try:
                gesture = msg.payload.decode().strip()
                self.messages_received += 1
                self.gesture_handler.handle_gesture(gesture)
            except Exception as e:
                print(f"❌ Error processing MQTT message: {e}")
                self.errors += 1
        
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        
        client.connect(self.mqtt_broker, 1883, 60)
        
        while self.running:
            client.loop()
            time.sleep(0.01)
        
        client.disconnect()
    
    def _listen_serial(self):
        """Listen for gestures via serial port"""
        try:
            import serial
            import serial.tools.list_ports
        except ImportError:
            print("❌ pyserial not installed. Install with: pip install pyserial")
            return
        
        # Auto-detect serial port if not specified
        if self.serial_port is None:
            ports = list(serial.tools.list_ports.comports())
            if not ports:
                print("❌ No serial ports found")
                return
            self.serial_port = ports[0].device
            print(f"ℹ️ Using serial port: {self.serial_port}")
        
        try:
            ser = serial.Serial(self.serial_port, 115200, timeout=1)
            print(f"✓ Connected to serial port {self.serial_port}")
            time.sleep(2)  # Wait for serial connection to stabilize
            
            while self.running:
                try:
                    line = ser.readline().decode(errors='ignore').strip()
                    if line:
                        self.messages_received += 1
                        self.gesture_handler.handle_gesture(line)
                except Exception as e:
                    print(f"❌ Serial read error: {e}")
                    self.errors += 1
        
        except Exception as e:
            print(f"❌ Serial connection error: {e}")
        
        finally:
            if ser.is_open:
                ser.close()
    
    def get_statistics(self):
        """Get listener statistics"""
        return {
            "running": self.running,
            "mode": self.input_mode,
            "messages_received": self.messages_received,
            "errors": self.errors,
        }
    
    def print_statistics(self):
        """Print listener statistics"""
        stats = self.get_statistics()
        print("\n" + "="*50)
        print("Gesture Listener Statistics")
        print("="*50)
        print(f"Mode: {stats['mode'].upper()}")
        print(f"Running: {stats['running']}")
        print(f"Messages received: {stats['messages_received']}")
        print(f"Errors: {stats['errors']}")
        print("="*50 + "\n")


# Example usage
if __name__ == "__main__":
    print("""
    This module is imported by main.py for gesture control integration.
    
    To test gesture handling:
    
    from gesture_control import GestureHandler, GestureType
    from viewport_generator import FourWayViewportGenerator
    
    viewport = FourWayViewportGenerator()
    handler = GestureHandler(viewport)
    
    # Simulate gestures
    handler.handle_gesture("UP")
    handler.handle_gesture("LEFT")
    handler.handle_gesture("NEAR")
    """)
