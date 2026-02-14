"""
4-Way Viewport Generator Examples
Demonstrates Pepper's Ghost holographic visualization system

Examples show:
1. Basic 4-way quad layout
2. Alternative layout modes (horizontal, vertical)
3. Adding reference geometry (axes, bounding box)
4. Viewport switching and control
"""

import sys
from dicom_loader import DICOMLoader
from vtk_visualizer import VTKVisualizer
from viewport_generator import FourWayViewportGenerator, ViewportLayout


def example_quad_layout(data_path):
    """Basic 4-way quad layout (2x2 grid)"""
    print("\n" + "="*60)
    print("Example 1: Quad Layout (2x2 Grid)")
    print("="*60)
    print("This is the standard layout for Pepper's Ghost")
    print("pyramid projection with 4 viewers around the display.\n")
    
    # Load DICOM
    loader = DICOMLoader()
    files = loader.load_folder(data_path)
    
    if loader.file_count == 0:
        print("❌ No DICOM files found")
        return False
    
    print(f"✓ Loaded {loader.file_count} DICOM files")
    
    # Create base visualizer
    viz = VTKVisualizer()
    if not viz.create_volume_from_dicom(loader, use_surface_rendering=False):
        print("❌ Failed to create volume")
        return False
    
    # Create 4-way viewport with quad layout
    viewport_system = FourWayViewportGenerator(
        window_title="HoloMed - Quad Layout (2x2)",
        layout=ViewportLayout.QUAD
    )
    
    # Add volume to all viewports
    viewport_system.add_volume(viz.volume_actor)
    
    print("✓ 4-way viewport initialized")
    print("Layout: Top-left (Bottom), Top-right (Right)")
    print("        Bottom-left (Left), Bottom-right (Top/Inverted)\n")
    
    viewport_system.show()
    return True


def example_horizontal_layout(data_path):
    """Horizontal 1x4 layout"""
    print("\n" + "="*60)
    print("Example 2: Horizontal Layout (1x4)")
    print("="*60)
    print("Shows all 4 views in a horizontal strip.\n")
    
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
    
    viewport_system = FourWayViewportGenerator(
        window_title="HoloMed - Horizontal Layout (1x4)",
        layout=ViewportLayout.HORIZONTAL
    )
    
    viewport_system.add_volume(viz.volume_actor)
    
    print("✓ 4-way viewport initialized")
    print("Layout: Bottom | Right | Top | Left (left to right)\n")
    
    viewport_system.show()
    return True


def example_vertical_layout(data_path):
    """Vertical 4x1 layout"""
    print("\n" + "="*60)
    print("Example 3: Vertical Layout (4x1)")
    print("="*60)
    print("Shows all 4 views in a vertical stack.\n")
    
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
    
    viewport_system = FourWayViewportGenerator(
        window_title="HoloMed - Vertical Layout (4x1)",
        layout=ViewportLayout.VERTICAL
    )
    
    viewport_system.add_volume(viz.volume_actor)
    
    print("✓ 4-way viewport initialized")
    print("Layout: Bottom (top)")
    print("        Right")
    print("        Top")
    print("        Left (bottom)\n")
    
    viewport_system.show()
    return True


def example_with_reference_geometry(data_path):
    """4-way viewport with reference geometry"""
    print("\n" + "="*60)
    print("Example 4: With Reference Geometry")
    print("="*60)
    print("Adds coordinate axes and bounding box for reference.\n")
    
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
    
    viewport_system = FourWayViewportGenerator(
        window_title="HoloMed - With Reference Geometry",
        layout=ViewportLayout.QUAD
    )
    
    # Add volume
    viewport_system.add_volume(viz.volume_actor)
    
    # Add coordinate axes to all viewports
    axes = viewport_system.create_axes_actor(scale=150)
    viewport_system.add_reference_geometry(axes)
    
    # Add bounding box (estimate from volume bounds)
    bbox = viewport_system.create_bounding_box_actor(
        bounds=(-200, 200, -200, 200, -200, 200)
    )
    viewport_system.add_reference_geometry(bbox)
    
    print("✓ 4-way viewport initialized with reference geometry")
    print("  • Coordinate axes (X=Red, Y=Green, Z=Blue)")
    print("  • Bounding box outline (gray)\n")
    
    viewport_system.show()
    return True


def example_single_viewport(data_path):
    """Single viewport debug mode"""
    print("\n" + "="*60)
    print("Example 5: Single Viewport (Debug Mode)")
    print("="*60)
    print("Shows only the bottom (normal) view for debugging.\n")
    
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
    
    viewport_system = FourWayViewportGenerator(
        window_title="HoloMed - Single Viewport (Debug)",
        layout=ViewportLayout.SINGLE
    )
    
    viewport_system.add_volume(viz.volume_actor)
    
    print("✓ 4-way viewport initialized (single view)")
    print("  • Showing only Bottom viewport\n")
    
    viewport_system.show()
    return True


def main():
    """Run examples"""
    print("\n" + "="*60)
    print("HoloMed 4-Way Viewport Generator Examples")
    print("="*60)
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run 4-way viewport examples"
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
        choices=[1, 2, 3, 4, 5],
        help="Which example to run (1-5)"
    )
    
    args = parser.parse_args()
    
    examples = {
        1: example_quad_layout,
        2: example_horizontal_layout,
        3: example_vertical_layout,
        4: example_with_reference_geometry,
        5: example_single_viewport,
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
    print("  python viewport_example.py --example 1  # Quad layout (standard)")
    print("  python viewport_example.py --example 2  # Horizontal layout")
    print("  python viewport_example.py --example 3  # Vertical layout")
    print("  python viewport_example.py --example 4  # With reference geometry")
    print("  python viewport_example.py --example 5  # Single viewport (debug)")
    print("  python viewport_example.py --data-path ./path/to/dicom/\n")
    
    sys.exit(main())
