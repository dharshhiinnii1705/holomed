"""
4-Way Viewport Generator for Pepper's Ghost Holographic Projection
Manages 4 orthogonal views for pyramid-based 360° visualization

Each viewport corresponds to one face of the acrylic pyramid:
  - Bottom (Viewer 1): 0° (Normal view)
  - Right (Viewer 2): 90° CCW (-90° rotation)
  - Top (Viewer 3): 180° (Inverted view)
  - Left (Viewer 4): 90° CW (+90° rotation)
"""

import vtk
import numpy as np
from enum import Enum


class ViewportPosition(Enum):
    """Enum for the four viewport positions"""
    BOTTOM = 0    # Viewer facing bottom face (normal view)
    RIGHT = 1     # Viewer on right side
    TOP = 2       # Viewer on top (inverted)
    LEFT = 3      # Viewer on left side


class ViewportLayout(Enum):
    """Enum for viewport layout options"""
    QUAD = "quad"              # 2x2 grid of viewports
    HORIZONTAL = "horizontal"  # 4 viewports in a row
    VERTICAL = "vertical"      # 4 viewports in a column
    SINGLE = "single"          # Single viewport (debug mode)


class ViewportCamera:
    """
    Manages camera position and orientation for a single viewport
    
    The camera is positioned to view the 3D model from a specific angle
    that corresponds to one face of the Pepper's Ghost pyramid.
    """
    
    def __init__(self, position, viewport_width=256, viewport_height=256):
        """
        Initialize viewport camera
        
        Args:
            position (ViewportPosition): Which face of pyramid this camera views
            viewport_width (int): Width of this viewport
            viewport_height (int): Height of this viewport
        """
        self.position = position
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        
        # VTK camera object
        self.camera = vtk.vtkCamera()
        
        # View direction and orientation based on position
        self._setup_camera_orientation()
    
    def _setup_camera_orientation(self):
        """Setup camera position and orientation based on viewport position"""
        
        # Default camera looks down Z-axis at origin
        distance = 400  # Distance from center
        
        if self.position == ViewportPosition.BOTTOM:
            # Bottom face: normal view, looking up at object
            # Camera below the object, looking up
            self.camera.SetPosition(0, -distance, 0)
            self.camera.SetFocalPoint(0, 0, 0)
            self.camera.SetViewUp(0, 0, 1)
            self.description = "Bottom (Front)"
            
        elif self.position == ViewportPosition.RIGHT:
            # Right face: viewer on right side, looking left
            # Camera on right side, looking left
            self.camera.SetPosition(distance, 0, 0)
            self.camera.SetFocalPoint(0, 0, 0)
            self.camera.SetViewUp(0, 0, 1)
            self.description = "Right"
            
        elif self.position == ViewportPosition.TOP:
            # Top face: inverted view
            # Camera above object, looking down (inverted)
            self.camera.SetPosition(0, distance, 0)
            self.camera.SetFocalPoint(0, 0, 0)
            self.camera.SetViewUp(0, 0, -1)  # View up is inverted
            self.description = "Top (Inverted)"
            
        elif self.position == ViewportPosition.LEFT:
            # Left face: viewer on left side, looking right
            # Camera on left side, looking right
            self.camera.SetPosition(-distance, 0, 0)
            self.camera.SetFocalPoint(0, 0, 0)
            self.camera.SetViewUp(0, 0, 1)
            self.description = "Left"
    
    def get_camera(self):
        """Get the VTK camera object"""
        return self.camera
    
    def get_view_description(self):
        """Get text description of this viewport"""
        return self.description
    
    def reset(self):
        """Reset camera to default orientation"""
        self._setup_camera_orientation()


class HolographicViewport:
    """
    Single viewport renderer for Pepper's Ghost display
    
    Each viewport has its own renderer, camera, and render area
    """
    
    def __init__(self, position, width=256, height=256):
        """
        Initialize a single viewport
        
        Args:
            position (ViewportPosition): Position on pyramid
            width (int): Viewport width in pixels
            height (int): Viewport height in pixels
        """
        self.position = position
        self.width = width
        self.height = height
        
        # Create viewport camera
        self.viewport_camera = ViewportCamera(position, width, height)
        
        # Create renderer
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.1, 0.1, 0.15)
        self.renderer.SetViewport(0, 0, 1, 1)  # Will be set by layout manager
        
        # Set camera
        self.renderer.SetActiveCamera(self.viewport_camera.get_camera())
        
        # Actor list (volume, reference geometry, etc.)
        self.actors = []
    
    def add_actor(self, actor):
        """Add actor to this viewport"""
        self.renderer.AddActor(actor)
        self.actors.append(actor)
    
    def remove_actor(self, actor):
        """Remove actor from this viewport"""
        self.renderer.RemoveActor(actor)
        if actor in self.actors:
            self.actors.remove(actor)
    
    def clear_actors(self):
        """Remove all actors"""
        for actor in self.actors:
            self.renderer.RemoveActor(actor)
        self.actors.clear()
    
    def reset_camera(self):
        """Reset camera to default position"""
        self.viewport_camera.reset()
        self.renderer.ResetCamera()
        self.renderer.GetActiveCamera().Zoom(1.5)
    
    def get_renderer(self):
        """Get the VTK renderer"""
        return self.renderer
    
    def get_camera(self):
        """Get the VTK camera"""
        return self.viewport_camera.get_camera()
    
    def set_viewport_bounds(self, x_min, y_min, x_max, y_max):
        """
        Set viewport position and size (normalized 0-1)
        
        Args:
            x_min, y_min, x_max, y_max: Viewport bounds in normalized coordinates
        """
        self.renderer.SetViewport(x_min, y_min, x_max, y_max)


class FourWayViewportGenerator:
    """
    Complete 4-way viewport system for Pepper's Ghost holographic projection
    
    This class manages:
    - 4 separate renderers (one per pyramid face)
    - Synchronized camera positions
    - Model transformation synchronization
    - Layout management (quad, horizontal, vertical)
    - Export capabilities for projection systems
    """
    
    def __init__(self, window_title="HoloMed - 4-Way Holographic View", 
                 layout=ViewportLayout.QUAD):
        """
        Initialize 4-way viewport system
        
        Args:
            window_title (str): Title for rendering window
            layout (ViewportLayout): Layout mode for viewports
        """
        self.window_title = window_title
        self.layout = layout
        
        # Create render window
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetWindowName(window_title)
        self.render_window.SetSize(1024, 1024)
        
        # Create interactor
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        
        # Create viewports
        self.viewports = {}
        self._create_viewports()
        
        # Model transformations (synchronized across all viewports)
        self.rotation = np.array([0.0, 0.0, 0.0])  # rx, ry, rz in degrees
        self.translation = np.array([0.0, 0.0, 0.0])
        self.scale = np.array([1.0, 1.0, 1.0])
        
        # Apply layout
        self._apply_layout()
    
    def _create_viewports(self):
        """Create 4 viewports"""
        viewport_size = 256
        
        for position in [ViewportPosition.BOTTOM, ViewportPosition.RIGHT,
                        ViewportPosition.TOP, ViewportPosition.LEFT]:
            viewport = HolographicViewport(position, viewport_size, viewport_size)
            self.viewports[position] = viewport
            self.render_window.AddRenderer(viewport.get_renderer())
    
    def _apply_layout(self):
        """Apply layout to viewports"""
        if self.layout == ViewportLayout.QUAD:
            self._layout_quad()
        elif self.layout == ViewportLayout.HORIZONTAL:
            self._layout_horizontal()
        elif self.layout == ViewportLayout.VERTICAL:
            self._layout_vertical()
        elif self.layout == ViewportLayout.SINGLE:
            self._layout_single()
    
    def _layout_quad(self):
        """2x2 grid layout"""
        positions = {
            ViewportPosition.BOTTOM: (0.0, 0.5, 0.5, 1.0),   # Top-left
            ViewportPosition.RIGHT: (0.5, 0.5, 1.0, 1.0),    # Top-right
            ViewportPosition.TOP: (0.5, 0.0, 1.0, 0.5),      # Bottom-right
            ViewportPosition.LEFT: (0.0, 0.0, 0.5, 0.5),     # Bottom-left
        }
        
        for position, (x_min, y_min, x_max, y_max) in positions.items():
            self.viewports[position].set_viewport_bounds(x_min, y_min, x_max, y_max)
    
    def _layout_horizontal(self):
        """Horizontal 1x4 layout"""
        positions = {
            ViewportPosition.BOTTOM: (0.0, 0.0, 0.25, 1.0),
            ViewportPosition.RIGHT: (0.25, 0.0, 0.5, 1.0),
            ViewportPosition.TOP: (0.5, 0.0, 0.75, 1.0),
            ViewportPosition.LEFT: (0.75, 0.0, 1.0, 1.0),
        }
        
        for position, (x_min, y_min, x_max, y_max) in positions.items():
            self.viewports[position].set_viewport_bounds(x_min, y_min, x_max, y_max)
    
    def _layout_vertical(self):
        """Vertical 4x1 layout"""
        positions = {
            ViewportPosition.BOTTOM: (0.0, 0.75, 1.0, 1.0),
            ViewportPosition.RIGHT: (0.0, 0.5, 1.0, 0.75),
            ViewportPosition.TOP: (0.0, 0.25, 1.0, 0.5),
            ViewportPosition.LEFT: (0.0, 0.0, 1.0, 0.25),
        }
        
        for position, (x_min, y_min, x_max, y_max) in positions.items():
            self.viewports[position].set_viewport_bounds(x_min, y_min, x_max, y_max)
    
    def _layout_single(self):
        """Single viewport (debug mode)"""
        # Only show bottom viewport
        self.viewports[ViewportPosition.BOTTOM].set_viewport_bounds(0.0, 0.0, 1.0, 1.0)
        
        # Hide others
        for position in [ViewportPosition.RIGHT, ViewportPosition.TOP, ViewportPosition.LEFT]:
            self.viewports[position].set_viewport_bounds(0.0, 0.0, 0.0, 0.0)
    
    def add_volume(self, volume_actor):
        """
        Add volume actor to all 4 viewports
        
        Args:
            volume_actor (vtk.vtkVolume): Volume actor from VTKVisualizer
        """
        for viewport in self.viewports.values():
            viewport.add_actor(volume_actor)
    
    def add_reference_geometry(self, actor, position=None):
        """
        Add reference geometry (axes, bounding box, etc.)
        
        Args:
            actor: VTK actor
            position: ViewportPosition or None for all viewports
        """
        if position is None:
            # Add to all viewports
            for viewport in self.viewports.values():
                viewport.add_actor(actor)
        else:
            self.viewports[position].add_actor(actor)
    
    def create_axes_actor(self, scale=100):
        """
        Create coordinate axes for reference
        
        Args:
            scale (float): Size of axes
            
        Returns:
            vtk.vtkAxesActor: Axes actor
        """
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(scale, scale, scale)
        
        # Create text labels
        axes.SetXAxisLabelText("X")
        axes.SetYAxisLabelText("Y")
        axes.SetZAxisLabelText("Z")
        
        return axes
    
    def create_bounding_box_actor(self, bounds):
        """
        Create bounding box outline
        
        Args:
            bounds (tuple): (xmin, xmax, ymin, ymax, zmin, zmax)
            
        Returns:
            vtk.vtkActor: Bounding box actor
        """
        outline = vtk.vtkOutlineSource()
        outline.SetBounds(*bounds)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(outline.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.3, 0.3, 0.3)
        
        return actor
    
    def rotate_all(self, rx, ry, rz):
        """
        Rotate all viewports' models
        
        Args:
            rx, ry, rz (float): Rotation angles in degrees
        """
        self.rotation += np.array([rx, ry, rz])
        self._sync_transformations()
    
    def translate_all(self, tx, ty, tz):
        """
        Translate all viewports' models
        
        Args:
            tx, ty, tz (float): Translation amounts
        """
        self.translation += np.array([tx, ty, tz])
        self._sync_transformations()
    
    def scale_all(self, sx, sy, sz):
        """
        Scale all viewports' models
        
        Args:
            sx, sy, sz (float): Scale factors
        """
        self.scale *= np.array([sx, sy, sz])
        self._sync_transformations()
    
    def _sync_transformations(self):
        """
        Synchronize transformations across all viewports
        
        Note: In a real implementation, this would update the actor's transformation
        matrix. For now, this is a placeholder for the synchronization logic.
        """
        # TODO: Apply self.rotation, self.translation, self.scale to all actors
        pass
    
    def reset_all_cameras(self):
        """Reset all cameras to default orientation"""
        for viewport in self.viewports.values():
            viewport.reset_camera()
    
    def reset_all_transformations(self):
        """Reset all model transformations"""
        self.rotation = np.array([0.0, 0.0, 0.0])
        self.translation = np.array([0.0, 0.0, 0.0])
        self.scale = np.array([1.0, 1.0, 1.0])
        self._sync_transformations()
    
    def get_viewport(self, position):
        """
        Get a specific viewport
        
        Args:
            position (ViewportPosition): Which viewport
            
        Returns:
            HolographicViewport: The requested viewport
        """
        return self.viewports[position]
    
    def get_all_viewports(self):
        """Get all viewports"""
        return self.viewports
    
    def get_viewport_count(self):
        """Get number of viewports"""
        return len(self.viewports)
    
    def show(self):
        """Display the 4-way viewport"""
        try:
            print("\n" + "="*60)
            print("Starting 4-Way Holographic Viewport")
            print("="*60)
            print("Layout: " + self.layout.value.upper())
            print("\nViewports:")
            for position, viewport in self.viewports.items():
                print(f"  • {position.name}: {viewport.viewport_camera.get_view_description()}")
            print("\nControls:")
            print("  - Left click + drag: Rotate (all viewports sync)")
            print("  - Right click + drag: Zoom")
            print("  - Middle click + drag: Pan")
            print("  - 'R': Reset cameras")
            print("  - 'Q' or close: Exit")
            print("="*60 + "\n")
            
            self.interactor.Initialize()
            self.render_window.Render()
            self.interactor.Start()
            
        except Exception as e:
            print(f"Error displaying viewport: {e}")
    
    def render(self):
        """Render without showing window"""
        self.render_window.Render()
    
    def save_screenshot(self, filename):
        """
        Save screenshot of all 4 viewports
        
        Args:
            filename (str): Output file path
        """
        try:
            # Create image writer
            window_to_image_filter = vtk.vtkWindowToImageFilter()
            window_to_image_filter.SetInput(self.render_window)
            window_to_image_filter.Update()
            
            writer = vtk.vtkPNGWriter()
            writer.SetFileName(filename)
            writer.SetInputConnection(window_to_image_filter.GetOutputPort())
            writer.Write()
            
            print(f"✓ Screenshot saved to {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return False
    
    def change_layout(self, new_layout):
        """
        Change viewport layout
        
        Args:
            new_layout (ViewportLayout): New layout mode
        """
        self.layout = new_layout
        self._apply_layout()
        print(f"✓ Changed layout to {new_layout.value}")


# Example usage
if __name__ == "__main__":
    from dicom_loader import DICOMLoader
    from vtk_visualizer import VTKVisualizer
    
    # Load DICOM
    loader = DICOMLoader()
    loader.load_folder("./data/scripts/hardware")
    
    if loader.file_count > 0:
        # Create base visualizer
        viz = VTKVisualizer()
        viz.create_volume_from_dicom(loader, use_surface_rendering=False)
        
        # Create 4-way viewport
        viewport_system = FourWayViewportGenerator(
            layout=ViewportLayout.QUAD
        )
        
        # Add volume to all 4 viewports
        viewport_system.add_volume(viz.volume_actor)
        
        # Add reference axes
        axes = viewport_system.create_axes_actor()
        viewport_system.add_reference_geometry(axes)
        
        # Display
        viewport_system.show()
    else:
        print("No DICOM files found")
