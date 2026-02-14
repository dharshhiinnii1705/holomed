"""
4-Way Viewport Generator Documentation
Complete guide to HoloMed's holographic projection system

======================================================================
OVERVIEW - PEPPER'S GHOST PRINCIPLE
======================================================================

The Pepper's Ghost illusion is an optical effect created by a specially
shaped transparent pyramid. When a 3D model is displayed on a screen
placed below the pyramid, viewers surrounding the pyramid see a floating
holographic image in the center.

Key Requirements:
1. Display system (screen/projector) below the pyramid
2. Acrylic pyramid with 45° angled faces (light transmission)
3. Five synchronized viewports (1 on projector, 4 around pyramid base)
4. Viewer positions: Front (bottom), Right, Back (top), Left

======================================================================
4-WAY VIEWPORT SYSTEM ARCHITECTURE
======================================================================

The FourWayViewportGenerator creates 4 independent renderers, each with
a unique camera orientation that corresponds to one face of the pyramid:

┌─────────────────────────────────────────────────────────────────┐
│                      Pepper's Ghost Pyramid                     │
│                                                                 │
│                    ╱╲  (Acrylic transparent)                   │
│                   ╱  ╲                                         │
│                  ╱    ╲                                        │
│                 ╱      ╲                                       │
│                ╱────────╲                                      │
│                                                                 │
│          Float hologram visible from all sides                 │
│               (Projected from center below)                    │
└─────────────────────────────────────────────────────────────────┘

Camera Positions (Top-down view):
┌──────────────────────────────┐
│      BACK (Top)    [TOP]     │
│                              │
│ [LEFT]            [BOTTOM]   │
│ (Left)      Center (Front)   │
│                              │
│      FRONT [RIGHT]           │
│          (Right)             │
└──────────────────────────────┘

Viewport Names & Positions:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Position     | View Direction | Camera Position | For Viewer  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOTTOM       | Looking up      | (0, -400, 0)    | Front (bottom)
RIGHT        | Looking left    | (400, 0, 0)     | Right side
TOP          | Looking down    | (0, 400, 0)     | Back (top/inverted)
LEFT         | Looking right   | (-400, 0, 0)    | Left side
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

======================================================================
CLASS HIERARCHY
======================================================================

FourWayViewportGenerator (Main orchestrator)
├── HolographicViewport (Per-viewport manager) × 4
│   ├── ViewportCamera (Camera orientation & position)
│   │   └── VTK Camera object
│   └── VTK Renderer (rendering engine)
└── Layout Manager (Arranges 4 viewports on screen)
    ├── Quad Layout (2x2 grid) ← RECOMMENDED for Pepper's Ghost
    ├── Horizontal Layout (1x4 strip)
    ├── Vertical Layout (4x1 stack)
    └── Single Layout (debug mode)

======================================================================
LAYOUT MODES
======================================================================

1. QUAD LAYOUT (RECOMMENDED for Pepper's Ghost)
   ┌──────────┬──────────┐
   │ Bottom   │ Right    │
   │ (0,0.5)  │ (0.5,0.5)│
   ├──────────┼──────────┤
   │ Left     │ Top      │
   │ (0,0)    │ (0.5,0)  │
   └──────────┴──────────┘
   
   Use case: Standard 4-way display showing all views simultaneously
   Memory: 4 × (256×256) = 4 renderers

2. HORIZONTAL LAYOUT
   ┌─┬─┬─┬─┐
   │B│R│T│L│
   └─┴─┴─┴─┘
   
   Use case: Wide monitor display of all 4 views
   Memory: Same as quad

3. VERTICAL LAYOUT
   ┌───┐
   │ B │
   ├───┤
   │ R │
   ├───┤
   │ T │
   ├───┤
   │ L │
   └───┘
   
   Use case: Narrow/tall display
   Memory: Same as quad

4. SINGLE LAYOUT (Debug mode)
   ┌────────┐
   │ Bottom │
   │        │
   └────────┘
   
   Use case: Testing single viewport
   Memory: 1 renderer (other 3 hidden)

======================================================================
QUICK START
======================================================================

1. Basic 4-way usage:
   
   from viewport_generator import FourWayViewportGenerator, ViewportLayout
   from vtk_visualizer import VTKVisualizer
   from dicom_loader import DICOMLoader
   
   # Load and visualize
   loader = DICOMLoader()
   loader.load_folder("./data/dicom/")
   
   viz = VTKVisualizer()
   viz.create_volume_from_dicom(loader)
   
   # Create 4-way viewport
   viewport_system = FourWayViewportGenerator(layout=ViewportLayout.QUAD)
   viewport_system.add_volume(viz.volume_actor)
   viewport_system.show()

2. Run examples:
   python viewport_example.py --example 1  # Quad layout
   python viewport_example.py --example 4  # With reference geometry

======================================================================
VIEWPORT API REFERENCE
======================================================================

FourWayViewportGenerator Methods:
─────────────────────────────────────────────────────────────────────

add_volume(volume_actor)
  Add a volume actor to all 4 viewports
  
add_reference_geometry(actor, position=None)
  Add reference geometry (axes, bounding box, etc.)
  - position=None: Add to all viewports
  - position=ViewportPosition.BOTTOM: Add to specific viewport

rotate_all(rx, ry, rz)
  Rotate models in all viewports
  - rx, ry, rz: Rotation amounts in degrees

translate_all(tx, ty, tz)
  Translate models in all viewports
  
scale_all(sx, sy, sz)
  Scale models in all viewports

reset_all_cameras()
  Reset all cameras to default orientation
  
reset_all_transformations()
  Reset all rotations, translations, scales

change_layout(new_layout)
  Switch between layout modes at runtime

get_viewport(position)
  Get specific HolographicViewport object

create_axes_actor(scale=100)
  Create coordinate axes for reference
  
create_bounding_box_actor(bounds)
  Create bounding box outline

show()
  Display interactive viewport

render()
  Render without showing window (headless)

save_screenshot(filename)
  Save 4-viewport as PNG image

======================================================================
TRANSFORMATION SYNCHRONIZATION
======================================================================

All 4 viewports display the SAME 3D model with synchronized transformations:

When you call rotate_all(10, 0, 0):
  ✓ Bottom viewport: Model rotates around X-axis
  ✓ Right viewport: Model rotates around X-axis  
  ✓ Top viewport: Model rotates around X-axis
  ✓ Left viewport: Model rotates around X-axis

The camera orientation for each preset view is FIXED, only the model moves.
This ensures that viewers on each side see the same model in sync.

State Variables:
  self.rotation = [rx, ry, rz]      # Accumulated rotation angles
  self.translation = [tx, ty, tz]   # Accumulated translations
  self.scale = [sx, sy, sz]         # Accumulated scale factors

======================================================================
GESTURE CONTROL INTEGRATION (FUTURE)
======================================================================

The following gesture inputs map to transformations:

  Gesture   → Transformation           → HoloMed Effect
  ─────────────────────────────────────────────────────────────
  UP        → rotate_all(5, 0, 0)      → Rotate "up" (tip toward viewer)
  DOWN      → rotate_all(-5, 0, 0)     → Rotate "down"
  LEFT      → rotate_all(0, 5, 0)      → Rotate "left"
  RIGHT     → rotate_all(0, -5, 0)     → Rotate "right"
  NEAR      → scale_all(1.1, 1.1, 1.1) → Zoom in/"step closer"
  FAR       → scale_all(0.9, 0.9, 0.9) → Zoom out/"step back"

Pseudo-code for integration:

  from gesture_mqtt_listener import gesture_listener
  from viewport_generator import FourWayViewportGenerator
  
  viewport = FourWayViewportGenerator()
  
  for gesture in gesture_listener:
    if gesture == "UP":
      viewport.rotate_all(5, 0, 0)
    elif gesture == "NEAR":
      viewport.scale_all(1.1, 1.1, 1.1)
    # ... etc
    viewport.render()

======================================================================
REFERENCE GEOMETRY
======================================================================

The system includes helper functions to add reference visualizations:

1. Coordinate Axes
   - Red line = X-axis
   - Green line = Y-axis
   - Blue line = Z-axis
   Uses right-hand coordinate system
   
   axes = viewport_system.create_axes_actor(scale=150)
   viewport_system.add_reference_geometry(axes)

2. Bounding Box
   - Gray outline box showing volume extents
   - Useful for spatial reference
   
   bbox = viewport_system.create_bounding_box_actor(
     bounds=(-200, 200, -200, 200, -200, 200)
   )
   viewport_system.add_reference_geometry(bbox)

3. Custom Geometry
   Any VTK actor can be added:
   
   viewport_system.add_reference_geometry(
     custom_actor,
     position=ViewportPosition.BOTTOM  # Optional: specific viewport
   )

======================================================================
PERFORMANCE CONSIDERATIONS
======================================================================

1. Rendering 4 viewports simultaneously:
   - 4× GPU load compared to single viewport
   - Modern GPUs handle this easily (60+ FPS)
   - Mid-range GPU target: 30+ FPS for real-time gesture control

2. Memory usage:
   - Volume data: Shared across all 4 renderers
   - Render buffers: 4× (each viewport has own framebuffer)
   - Typical: 2-4 GB for medical imaging workflows

3. Optimization strategies:
   - Use surface rendering (--surface flag) for faster iteration
   - Reduce volume resolution if needed
   - Use single layout for debugging individual viewport
   - Disable reference geometry if not needed

======================================================================
TROUBLESHOOTING
======================================================================

Issue: Only one viewport is visible
Solution: Check layout mode. For quad layout, all 4 should show.
         Use example 5 (single layout) for intentional single view.

Issue: Models don't move together in all views
Solution: Use rotate_all/translate_all methods
         Manual camera movement won't sync across all 4

Issue: Gestures not controlling rotation
Solution: Gesture integration is in gesture_mqtt_listener.py
         Need to add callback to viewport_system methods

Issue: Screenshot distorted
Solution: Ensure viewport_system is fully rendered before saving
         Call render() before save_screenshot()

======================================================================
NEXT STEPS
======================================================================

1. [IN PROGRESS] Gesture control loop integration
2. [TODO] Real-time latency optimization (<50ms)
3. [TODO] Pepper's Ghost pyramid calibration tool
4. [TODO] Screen projection mapping (if using external display)
5. [TODO] Multi-gesture sequences (swipe, pinch, roll)

======================================================================
"""

# This file is documentation only
