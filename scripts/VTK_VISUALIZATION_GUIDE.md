"""
VTK Visualization Integration Guide
Complete documentation for volumetric reconstruction and rendering

======================================================================
OVERVIEW
======================================================================

The VTKVisualizer module provides:
1. 3D volumetric reconstruction from DICOM slices
2. GPU-accelerated volume rendering using ray casting
3. Alternative surface rendering via marching cubes algorithm
4. Real-time transformation controls (rotation, translation, scaling)
5. Medical imaging windowing/leveling support
6. Interactive camera control with gesture integration hooks

======================================================================
QUICK START
======================================================================

1. Load DICOM data and visualize:
   
   python main.py --data-path ./data/sample_dicom/
   
2. Use surface rendering instead of volume rendering:
   
   python main.py --data-path ./data/sample_dicom/ --surface

3. Programmatic usage:
   
   from dicom_loader import DICOMLoader
   from vtk_visualizer import VTKVisualizer
   
   # Load DICOM
   loader = DICOMLoader()
   loader.load_folder("./data/sample_dicom/")
   
   # Create and display visualization
   viz = VTKVisualizer()
   viz.create_volume_from_dicom(loader)
   viz.show()

======================================================================
ARCHITECTURE
======================================================================

VTKVisualizer Class Structure:
├── __init__()                    # Initialize render window/interactor
├── create_volume_from_dicom()    # Main entry point
├── _stack_dicom_slices()         # Stack 2D slices into 3D volume
├── _numpy_to_vtk_image()         # Convert numpy array to VTK format
├── _render_volume()              # GPU volume rendering
├── _render_surface()             # Marching cubes surface rendering
├── Transformation Methods:
│   ├── rotate_model()            # Rotation (for gesture control)
│   ├── translate_model()         # Translation
│   └── scale_model()             # Scaling
├── set_windowing()               # Medical imaging window/level
├── Camera Controls:
│   ├── get_camera()
│   ├── reset_camera()
│   └── show()
└── Internal State:
    ├── volume_mapper (vtkGPUVolumeRayCastMapper)
    ├── volume_actor (vtkVolume)
    ├── renderer (vtkRenderer)
    └── interactor (vtkRenderWindowInteractor)

======================================================================
RENDERING MODES
======================================================================

1. VOLUME RENDERING (Default - Recommended)
   - Uses GPU-accelerated ray casting
   - Supports transparency and gradient-based shading
   - Better for exploring internal structures
   - Slightly slower (~30-60 FPS on modern GPUs)
   
   viz.create_volume_from_dicom(loader, use_surface_rendering=False)

2. SURFACE RENDERING (Alternative)
   - Marching cubes algorithm extracts surface mesh
   - Faster rendering (~200+ FPS)
   - Better for 3D printing/external visualization
   - Less detailed internal information
   
   viz.create_volume_from_dicom(loader, use_surface_rendering=True)

======================================================================
TRANSFER FUNCTIONS (Color & Opacity)
======================================================================

The volume rendering uses:
- Color Transfer Function: Maps intensity to color
  • 0 → Black (background)
  • 100 → Blue (soft tissue)
  • 150 → Orange (denser tissue)
  • 200 → Yellow (bone/dense)
  • 255 → White (very dense)

- Opacity Function: Maps intensity to transparency
  • 0 → Fully transparent
  • 50-200 → Gradually opaque
  • 255 → Fully opaque

These can be customized by modifying _render_volume():
    opacity_func = vtk.vtkPiecewiseFunction()
    opacity_func.AddPoint(value, opacity)  # 0.0=transparent, 1.0=opaque

======================================================================
GESTURE CONTROL INTEGRATION
======================================================================

The model transformation methods are designed for gesture input:

From gesture_mqtt_listener.py / gesture_serial.py:

    gesture_data = receive_gesture()  # "UP", "DOWN", "LEFT", "RIGHT"
    
    gesture_to_rotation = {
        "UP": (10, 0, 0),      # Rotate around X-axis
        "DOWN": (-10, 0, 0),
        "LEFT": (0, 10, 0),    # Rotate around Y-axis
        "RIGHT": (0, -10, 0),
        "NEAR": (0, 0, 0),     # Z-scaling (pinch)
        "FAR": (0, 0, 0)       # Z-scaling (spread)
    }
    
    if gesture_data in gesture_to_rotation:
        rx, ry, rz = gesture_to_rotation[gesture_data]
        viz.rotate_model(rx, ry, rz)
        viz.render_window.Render()  # Refresh display

======================================================================
INTERACTIVE CONTROLS (Mouse)
======================================================================

In the VTK window:
- Left Click + Drag    : Rotate model (arcball style)
- Right Click + Drag   : Zoom in/out
- Middle Click + Drag  : Pan (translate)
- 'R'                  : Reset view
- 'Q' or Close Window  : Exit

======================================================================
WINDOWING/LEVELING (Medical Imaging)
======================================================================

DICOM typically uses windowing to enhance contrast:

    viz.set_windowing(window_center=50, window_width=400)

Common presets:
- Soft Tissue:   center=50,   width=400
- Bone:          center=400,  width=2000
- Lung:          center=-400, width=1500
- Brain:         center=40,   width=80
- Head/Neck:     center=50,   width=350

======================================================================
PERFORMANCE OPTIMIZATION
======================================================================

For real-time gesture control (<50ms latency):

1. GPU Volume Rendering (faster)
   - Uses vtkGPUVolumeRayCastMapper
   - Requires modern GPU (NVIDIA, AMD, Intel)
   - 60+ FPS on mid-range GPUs

2. Surface Rendering (fastest)
   - Use --surface flag for marching cubes
   - 200+ FPS on most machines
   - Better for Pepper's Ghost latency requirements

3. Reduce Resolution
   - Downsample volume before rendering
   - Implement in vtk_visualizer.py:
     volume_data = volume_data[::2, ::2, ::2]

======================================================================
PEPPER'S GHOST PROJECTION
======================================================================

For the acrylic pyramid projection system:

1. The 4-way viewport generator will split the scene into 4 views
2. Apply horizontal/vertical flip transforms:
   
   # Bottom face (viewer 1 - normal)
   # Renderer 0: Normal
   
   # Right face (viewer 2 - rotated left)
   # Renderer 1: 90° counter-clockwise
   
   # Top face (viewer 3 - inverted)
   # Renderer 2: 180° rotation
   
   # Left face (viewer 4 - rotated right)
   # Renderer 3: 90° clockwise

3. Each renderer same 3D model with different camera angles
4. Acrylic pyramid mirror projects to 360° floating display

======================================================================
TROUBLESHOOTING
======================================================================

Issue: "APDS-9960 init failed" or module not found
Solution: pip install vtk numpy pydicom pillow scipy

Issue: No rendering window appears
Solution: Check if DICOM files exist in data path
         Verify graphics drivers are updated

Issue: Low FPS (<30 fps)
Solution: Use --surface flag for faster rendering
         Update GPU drivers
         Reduce volume resolution

Issue: Colors look wrong
Solution: Adjust transfer functions in _render_volume()
         Check window/level settings
         Verify DICOM data is not corrupted

======================================================================
NEXT STEPS
======================================================================

1. [TODO] Create 4-way viewport generator for Pepper's Ghost
2. [TODO] Integrate gesture control loop
3. [TODO] Add MQTT/Serial listener callbacks
4. [TODO] Implement real-time transformation pipeline
5. [IN PROGRESS] Add error handling and logging
6. [TODO] Create unit tests for transformations
7. [TODO] Optimize for <50ms gesture latency

======================================================================
"""

# This file is documentation only - run main.py to start visualization
