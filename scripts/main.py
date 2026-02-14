"""
HoloMed - Main Application
Combines VTK 3D visualization with gesture control from ESP32 sensor
"""

import sys
import os
import argparse
from dicom_loader import DICOMLoader
from vtk_visualizer import VTKVisualizer
from viewport_generator import FourWayViewportGenerator, ViewportLayout
from gesture_control import GestureHandler, GestureListenerThread


def print_header():
    """Display application header"""
    print("\n" + "="*60)
    print("🏥 HoloMed - Medical Imaging with Gesture Control")
    print("="*60)
    print("Low-cost holographic visualization system")
    print("3D volumetric reconstruction + Pepper's Ghost projection")
    print("="*60 + "\n")


def load_dicom_data(data_path):
    """
    Load DICOM files from specified path
    
    Args:
        data_path (str): Path to DICOM directory
        
    Returns:
        DICOMLoader: Loaded DICOM data or None on failure
    """
    print(f"📁 Loading DICOM files from: {data_path}")
    
    loader = DICOMLoader()
    files = loader.load_folder(data_path)
    
    if loader.file_count == 0:
        print("❌ No DICOM files found in the specified directory")
        return None
    
    print(f"✓ Successfully loaded {loader.file_count} DICOM files\n")
    
    # Display metadata from first file
    info = loader.get_info(0)
    print("First file information:")
    for key, value in info.items():
        print(f"  • {key}: {value}")
    print()
    
    return loader


def initialize_visualization(loader, use_surface=False):
    """
    Initialize VTK visualization from DICOM data
    
    Args:
        loader (DICOMLoader): Loaded DICOM data
        use_surface (bool): Use surface rendering instead of volume rendering
        
    Returns:
        VTKVisualizer: Initialized visualizer or None on failure
    """
    print("🎨 Initializing VTK 3D visualization...")
    
    viz = VTKVisualizer("HoloMed 3D Volume Visualization")
    
    if not viz.create_volume_from_dicom(loader, use_surface_rendering=use_surface):
        print("❌ Failed to create 3D volume")
        return None
    
    print("✓ VTK visualization initialized\n")
    return viz


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="HoloMed - Medical imaging holographic visualization"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        help="Path to DICOM file directory"
    )
    parser.add_argument(
        "--surface",
        action="store_true",
        help="Use surface rendering (marching cubes) instead of volume rendering"
    )
    parser.add_argument(
        "--holographic",
        action="store_true",
        help="Enable 4-way Pepper's Ghost holographic projection view"
    )
    parser.add_argument(
        "--layout",
        type=str,
        choices=["quad", "horizontal", "vertical", "single"],
        default="quad",
        help="Viewport layout for holographic mode (default: quad)"
    )
    parser.add_argument(
        "--gesture",
        action="store_true",
        help="Enable real-time gesture control from ESP32"
    )
    parser.add_argument(
        "--gesture-input",
        type=str,
        choices=["mqtt", "serial"],
        default="mqtt",
        help="Gesture input method: mqtt (wireless) or serial (USB)"
    )
    parser.add_argument(
        "--mqtt-broker",
        type=str,
        default="192.168.1.10",
        help="MQTT broker IP address (default: 192.168.1.10)"
    )
    parser.add_argument(
        "--serial-port",
        type=str,
        help="Serial port for gesture input (e.g., COM3, /dev/ttyUSB0)"
    )
    
    args = parser.parse_args()
    
    print_header()
    
    # Determine data path
    if args.data_path:
        data_path = args.data_path
    else:
        # Default to data/scripts/hardware
        data_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "data", "scripts", "hardware"
        )
    
    # Load DICOM data
    loader = load_dicom_data(data_path)
    if loader is None:
        print("💡 Tip: Ensure DICOM files (.dcm) are in the specified directory")
        return 1
    
    # Initialize visualization
    viz = initialize_visualization(loader, use_surface=args.surface)
    if viz is None:
        return 1
    
    # Choose display mode
    if args.holographic:
        return _run_holographic_mode(viz, args.layout, args.gesture, args.gesture_input, args.mqtt_broker, args.serial_port)
    else:
        return _run_standard_mode(viz)


def _run_standard_mode(viz):
    """Run standard single-window visualization"""
    try:
        viz.show()
    except KeyboardInterrupt:
        print("\n👋 Closing visualization...")
    except Exception as e:
        print(f"❌ Visualization error: {e}")
        return 1
    
    print("✓ HoloMed visualization closed successfully\n")
    return 0


def _run_holographic_mode(viz, layout_name, enable_gesture=False, gesture_input="mqtt", 
                         mqtt_broker="192.168.1.10", serial_port=None):
    """
    Run 4-way Pepper's Ghost holographic projection mode
    
    Args:
        viz (VTKVisualizer): Initialized visualizer
        layout_name (str): Layout mode name
        enable_gesture (bool): Enable real-time gesture control
        gesture_input (str): "mqtt" or "serial"
        mqtt_broker (str): MQTT broker IP
        serial_port (str): Serial port name
        
    Returns:
        int: Exit code
    """
    print("\n🎭 Entering Holographic Projection Mode")
    print("="*50)
    
    # Map layout name to enum
    layout_map = {
        "quad": ViewportLayout.QUAD,
        "horizontal": ViewportLayout.HORIZONTAL,
        "vertical": ViewportLayout.VERTICAL,
        "single": ViewportLayout.SINGLE,
    }
    
    layout = layout_map.get(layout_name, ViewportLayout.QUAD)
    
    try:
        # Create 4-way viewport system
        viewport_system = FourWayViewportGenerator(
            window_title="HoloMed - Pepper's Ghost Holographic Projection",
            layout=layout
        )
        
        # Add volume to all 4 viewports
        viewport_system.add_volume(viz.volume_actor)
        
        # Add reference geometry
        axes = viewport_system.create_axes_actor(scale=150)
        viewport_system.add_reference_geometry(axes)
        
        print(f"✓ 4-way viewport initialized")
        print(f"✓ Layout: {layout_name.upper()}")
        print(f"✓ Viewports: BOTTOM | RIGHT | TOP | LEFT")
        
        # Setup gesture control if enabled
        listener = None
        if enable_gesture:
            print(f"\n🎮 Gesture Control Enabled")
            print(f"  Input: {gesture_input.upper()}")
            
            if gesture_input == "mqtt":
                print(f"  Broker: {mqtt_broker}")
            elif gesture_input == "serial":
                print(f"  Port: {serial_port or 'Auto-detect'}")
            
            # Create gesture handler
            handler = GestureHandler(viewport_system)
            
            # Create and start listener
            listener = GestureListenerThread(
                handler,
                input_mode=gesture_input,
                mqtt_broker=mqtt_broker,
                serial_port=serial_port
            )
            
            print("\n  Starting gesture listener...")
            listener.start()
            print("  ✓ Ready for hand gestures (UP, DOWN, LEFT, RIGHT, NEAR, FAR)")
        
        print("="*50 + "\n")
        
        # Display
        viewport_system.show()
        
        # Print statistics if gesture control was enabled
        if listener:
            listener.stop()
            print()
            listener.print_statistics()
            handler.print_statistics()
    
    except KeyboardInterrupt:
        print("\n👋 Closing holographic view...")
        if listener and listener.running:
            listener.stop()
    except Exception as e:
        print(f"❌ Holographic display error: {e}")
        if listener and listener.running:
            listener.stop()
        return 1
    
    print("✓ HoloMed holographic projection closed successfully\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
