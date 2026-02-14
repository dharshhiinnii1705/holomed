"""
VTK Visualization Example
Demonstrates volume rendering and gesture-like transformations

This script shows:
1. How to load DICOM data
2. How to create a 3D volume visualization
3. How to apply transformations (useful for gesture control testing)
"""

import time
import sys
from dicom_loader import DICOMLoader
from vtk_visualizer import VTKVisualizer


def example_basic_visualization(data_path):
    """Basic volume visualization example"""
    print("\n" + "="*60)
    print("Example 1: Basic Volume Visualization")
    print("="*60)
    
    # Load DICOM
    loader = DICOMLoader()
    files = loader.load_folder(data_path)
    
    if loader.file_count == 0:
        print("❌ No DICOM files found")
        return False
    
    print(f"✓ Loaded {loader.file_count} DICOM files")
    
    # Create visualizer
    viz = VTKVisualizer("HoloMed Example - Basic Volume")
    
    # Create volume
    if not viz.create_volume_from_dicom(loader, use_surface_rendering=False):
        print("❌ Failed to create volume")
        return False
    
    print("✓ Click in window to close, or press 'Q'")
    viz.show()
    return True


def example_surface_rendering(data_path):
    """Surface rendering example (marching cubes)"""
    print("\n" + "="*60)
    print("Example 2: Surface Rendering with Marching Cubes")
    print("="*60)
    
    loader = DICOMLoader()
    files = loader.load_folder(data_path)
    
    if loader.file_count == 0:
        print("❌ No DICOM files found")
        return False
    
    print(f"✓ Loaded {loader.file_count} DICOM files")
    
    viz = VTKVisualizer("HoloMed Example - Surface Rendering")
    
    if not viz.create_volume_from_dicom(loader, use_surface_rendering=True):
        print("❌ Failed to create surface")
        return False
    
    print("✓ Click in window to close, or press 'Q'")
    viz.show()
    return True


def example_gesture_simulation(data_path):
    """Simulate gesture-based transformations"""
    print("\n" + "="*60)
    print("Example 3: Gesture-Based Rotation Simulation")
    print("="*60)
    print("This example simulates the gesture control system")
    print("The volume will automatically rotate to simulate gestures")
    
    loader = DICOMLoader()
    files = loader.load_folder(data_path)
    
    if loader.file_count == 0:
        print("❌ No DICOM files found")
        return False
    
    print(f"✓ Loaded {loader.file_count} DICOM files\n")
    
    viz = VTKVisualizer("HoloMed Example - Gesture Simulation")
    
    if not viz.create_volume_from_dicom(loader, use_surface_rendering=False):
        print("❌ Failed to create volume")
        return False
    
    print("Starting gesture simulation in 2 seconds...")
    print("Window will show rotating volume\n")
    time.sleep(2)
    
    # Simulate gesture sequence
    gestures = [
        ("UP", (5, 0, 0), "Rotating UP (around X-axis)"),
        ("DOWN", (-5, 0, 0), "Rotating DOWN (around X-axis)"),
        ("LEFT", (0, 5, 0), "Rotating LEFT (around Y-axis)"),
        ("RIGHT", (0, -5, 0), "Rotating RIGHT (around Y-axis)"),
    ]
    
    rotation_sequence = (
        gestures * 2  # Repeat sequence twice
    )
    
    # Note: Manual rotation simulation since we can't yield control to VTK
    # In real implementation, this would be in a separate gesture event loop
    print("Gesture simulation ready (interactive mode - manual rotation)")
    print("Use mouse to manually rotate:")
    print("  - Left click + drag: Rotate")
    print("  - Right click + drag: Zoom")
    print("  - 'Q': Exit\n")
    
    viz.show()
    return True


def example_windowing(data_path):
    """Demonstrate windowing/leveling"""
    print("\n" + "="*60)
    print("Example 4: Medical Imaging Windowing")
    print("="*60)
    
    loader = DICOMLoader()
    files = loader.load_folder(data_path)
    
    if loader.file_count == 0:
        print("❌ No DICOM files found")
        return False
    
    print(f"✓ Loaded {loader.file_count} DICOM files")
    
    viz = VTKVisualizer("HoloMed Example - Windowing")
    
    if not viz.create_volume_from_dicom(loader, use_surface_rendering=False):
        print("❌ Failed to create volume")
        return False
    
    # Apply soft tissue windowing
    print("\nApplying Soft Tissue windowing (center=50, width=400)")
    viz.set_windowing(window_center=50, window_width=400)
    
    print("✓ Click in window to close, or press 'Q'")
    print("  (Notice different contrast compared to default)")
    viz.show()
    return True


def main():
    """Run examples"""
    print("\n" + "="*60)
    print("HoloMed VTK Visualization Examples")
    print("="*60)
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run VTK visualization examples"
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
    
    args = parser.parse_args()
    
    examples = {
        1: example_basic_visualization,
        2: example_surface_rendering,
        3: example_gesture_simulation,
        4: example_windowing,
    }
    
    print(f"\nData path: {args.data_path}")
    print(f"Running example {args.example}...\n")
    
    try:
        success = examples[args.example](args.data_path)
        
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
    print("  python vtk_example.py --example 1  # Basic volume rendering")
    print("  python vtk_example.py --example 2  # Surface rendering")
    print("  python vtk_example.py --example 3  # Gesture simulation")
    print("  python vtk_example.py --example 4  # Windowing/leveling")
    print("  python vtk_example.py --data-path ./path/to/dicom/\n")
    
    sys.exit(main())
