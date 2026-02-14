"""
Gesture Control Examples
Demonstrates how to integrate real-time gesture input with HoloMed visualization

Examples show:
1. Basic gesture simulation (manual gesture input)
2. MQTT gesture listener (wireless from ESP32)
3. Serial gesture listener (USB from ESP32)
4. Multi-gesture sequence detection
5. Full interactive system (gesture + viewport + transformations)
"""

import sys
import time
from dicom_loader import DICOMLoader
from vtk_visualizer import VTKVisualizer
from viewport_generator import FourWayViewportGenerator, ViewportLayout
from gesture_control import GestureHandler, GestureListenerThread, GestureType


def example_gesture_simulation(data_path):
    """Simulate gestures programmatically"""
    print("\n" + "="*60)
    print("Example 1: Gesture Simulation")
    print("="*60)
    print("This example simulates gesture input without actual sensor\n")
    
    # Load DICOM and create viewport
    loader = DICOMLoader()
    files = loader.load_folder(data_path)
    
    if loader.file_count == 0:
        print("❌ No DICOM files found")
        return False
    
    print(f"✓ Loaded {loader.file_count} DICOM files")
    
    viz = VTKVisualizer()
    if not viz.create_volume_from_dicom(loader, use_surface_rendering=False):
        print("❌ Failed to create volume")
        return False
    
    # Create 4-way viewport
    viewport = FourWayViewportGenerator(layout=ViewportLayout.QUAD)
    viewport.add_volume(viz.volume_actor)
    
    # Create gesture handler
    handler = GestureHandler(viewport)
    
    print("✓ Gesture simulation ready\n")
    
    # Simulate gesture sequence
    print("Simulating gesture sequence:")
    print("-" * 40)
    
    gestures_sequence = [
        ("UP", 0.5),
        ("UP", 0.5),
        ("LEFT", 0.5),
        ("DOWN", 0.5),
        ("RIGHT", 0.5),
        ("NEAR", 0.8),
        ("FAR", 0.8),
    ]
    
    for gesture, delay in gestures_sequence:
        print(f"  Gesture: {gesture}")
        handler.handle_gesture(gesture)
        viewport.render()
        time.sleep(delay)
    
    print("-" * 40)
    print("\nShowing visualization with transformed model...")
    print("Press 'Q' or close window to exit\n")
    
    # Print statistics
    handler.print_statistics()
    
    # Show visualization
    viewport.show()
    return True


def example_mqtt_listener(data_path, mqtt_broker="192.168.1.10"):
    """Listen for gestures via MQTT from ESP32"""
    print("\n" + "="*60)
    print("Example 2: MQTT Gesture Listener")
    print("="*60)
    print("This example listens for gestures published via MQTT")
    print(f"MQTT Broker: {mqtt_broker}")
    print("Topic: holomed/gesture\n")
    
    # Check if paho-mqtt is installed
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        print("❌ paho-mqtt not installed")
        print("   Install with: pip install paho-mqtt")
        return False
    
    # Load DICOM and create viewport
    loader = DICOMLoader()
    files = loader.load_folder(data_path)
    
    if loader.file_count == 0:
        print("❌ No DICOM files found")
        return False
    
    print(f"✓ Loaded {loader.file_count} DICOM files")
    
    viz = VTKVisualizer()
    if not viz.create_volume_from_dicom(loader, use_surface_rendering=False):
        print("❌ Failed to create volume")
        return False
    
    # Create 4-way viewport
    viewport = FourWayViewportGenerator(layout=ViewportLayout.QUAD)
    viewport.add_volume(viz.volume_actor)
    
    # Create gesture handler
    handler = GestureHandler(viewport)
    
    # Create and start listener thread
    listener = GestureListenerThread(
        handler,
        input_mode="mqtt",
        mqtt_broker=mqtt_broker
    )
    
    print("✓ Starting MQTT gesture listener...")
    listener.start()
    
    print("\n" + "="*60)
    print("Ready to receive gestures from ESP32!")
    print("="*60)
    print("\nMake hand gestures in front of APDS-9960 sensor")
    print("Gestures: UP, DOWN, LEFT, RIGHT, NEAR, FAR")
    print("\nDisplaying 4-way viewport...")
    print("Press 'Q' or close window to exit\n")
    
    try:
        # Show viewport and process gestures concurrently
        viewport.show()
    
    except KeyboardInterrupt:
        print("\n👋 Closing...")
    
    finally:
        listener.stop()
        listener.print_statistics()
        handler.print_statistics()
    
    return True


def example_serial_listener(data_path, serial_port=None):
    """Listen for gestures via serial /USB from ESP32"""
    print("\n" + "="*60)
    print("Example 3: Serial Gesture Listener")
    print("="*60)
    print("This example listens for gestures via serial/USB")
    print(f"Serial Port: {serial_port or 'Auto-detect'}\n")
    
    # Check if pyserial is installed
    try:
        import serial
    except ImportError:
        print("❌ pyserial not installed")
        print("   Install with: pip install pyserial")
        return False
    
    # Load DICOM and create viewport
    loader = DICOMLoader()
    files = loader.load_folder(data_path)
    
    if loader.file_count == 0:
        print("❌ No DICOM files found")
        return False
    
    print(f"✓ Loaded {loader.file_count} DICOM files")
    
    viz = VTKVisualizer()
    if not viz.create_volume_from_dicom(loader, use_surface_rendering=False):
        print("❌ Failed to create volume")
        return False
    
    # Create 4-way viewport
    viewport = FourWayViewportGenerator(layout=ViewportLayout.QUAD)
    viewport.add_volume(viz.volume_actor)
    
    # Create gesture handler
    handler = GestureHandler(viewport)
    
    # Create and start listener thread
    listener = GestureListenerThread(
        handler,
        input_mode="serial",
        serial_port=serial_port
    )
    
    print("✓ Starting serial gesture listener...")
    listener.start()
    
    print("\n" + "="*60)
    print("Ready to receive gestures from ESP32!")
    print("="*60)
    print("\nMake hand gestures in front of APDS-9960 sensor")
    print("Gestures will be transmitted via USB serial")
    print("\nDisplaying 4-way viewport...")
    print("Press 'Q' or close window to exit\n")
    
    try:
        # Show viewport and process gestures concurrently
        viewport.show()
    
    except KeyboardInterrupt:
        print("\n👋 Closing...")
    
    finally:
        listener.stop()
        listener.print_statistics()
        handler.print_statistics()
    
    return True


def example_gesture_patterns(data_path):
    """Detect and respond to gesture patterns"""
    print("\n" + "="*60)
    print("Example 4: Gesture Pattern Detection")
    print("="*60)
    print("This example detects multi-gesture patterns\n")
    
    loader = DICOMLoader()
    files = loader.load_folder(data_path)
    
    if loader.file_count == 0:
        print("❌ No DICOM files found")
        return False
    
    print(f"✓ Loaded {loader.file_count} DICOM files")
    
    viz = VTKVisualizer()
    if not viz.create_volume_from_dicom(loader, use_surface_rendering=False):
        print("❌ Failed to create volume")
        return False
    
    viewport = FourWayViewportGenerator(layout=ViewportLayout.QUAD)
    viewport.add_volume(viz.volume_actor)
    
    handler = GestureHandler(viewport)
    
    print("✓ Gesture pattern detection ready\n")
    
    # Test gesture patterns
    patterns = [
        (["UP", "UP", "UP"], "Fast swipe UP"),
        (["LEFT", "LEFT", "LEFT"], "Fast swipe LEFT"),
        (["UP", "LEFT"], "Diagonal UP-LEFT"),
        (["DOWN", "RIGHT", "DOWN"], "Oscillation DOWN-RIGHT-DOWN"),
    ]
    
    print("Testing gesture patterns:")
    print("-" * 40)
    
    for gestures, expected_pattern in patterns:
        handler.reset_history()
        
        print(f"\nGestures: {' → '.join(gestures)}")
        print(f"Expected: {expected_pattern}")
        
        for gesture in gestures:
            handler.handle_gesture(gesture)
            viewport.render()
            time.sleep(0.3)
        
        detected_pattern = handler.detect_swipe()
        detected_str = detected_pattern if detected_pattern else "None"
        print(f"Detected: {detected_str}")
    
    print("-" * 40)
    print("\nShowing final viewport state...")
    print("Press 'Q' or close window to exit\n")
    
    viewport.show()
    return True


def main():
    """Run examples"""
    print("\n" + "="*60)
    print("HoloMed Gesture Control Examples")
    print("="*60)
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run gesture control examples"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="./data/scripts/hardware",
        help="Path to DICOM directory"
    )
    parser.add_argument(
        "--example",
        type=int,
        default=1,
        choices=[1, 2, 3, 4],
        help="Which example to run (1-4)"
    )
    parser.add_argument(
        "--mqtt-broker",
        type=str,
        default="192.168.1.10",
        help="MQTT broker address (for example 2)"
    )
    parser.add_argument(
        "--serial-port",
        type=str,
        help="Serial port (for example 3, auto-detect if not specified)"
    )
    
    args = parser.parse_args()
    
    examples = {
        1: (example_gesture_simulation, {"data_path": args.data_path}),
        2: (example_mqtt_listener, {"data_path": args.data_path, "mqtt_broker": args.mqtt_broker}),
        3: (example_serial_listener, {"data_path": args.data_path, "serial_port": args.serial_port}),
        4: (example_gesture_patterns, {"data_path": args.data_path}),
    }
    
    print(f"\nData path: {args.data_path}")
    print(f"Running example {args.example}...\n")
    
    try:
        example_func, example_args = examples[args.example]
        success = example_func(**example_args)
        
        if success:
            print("\n✓ Example completed successfully")
            return 0
        else:
            print("\n❌ Example failed")
            return 1
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    print("\nUsage Examples:")
    print("  python gesture_example.py --example 1  # Gesture simulation")
    print("  python gesture_example.py --example 2  # MQTT listener")
    print("  python gesture_example.py --example 3  # Serial listener")
    print("  python gesture_example.py --example 4  # Pattern detection")
    print("  python gesture_example.py --mqtt-broker 192.168.1.XX")
    print("  python gesture_example.py --serial-port COM3\n")
    
    sys.exit(main())
