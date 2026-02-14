"""
VTK Visualizer Module
Handles 3D volumetric reconstruction and rendering from DICOM slices
"""

import numpy as np
import vtk
from vtk.util import numpy_support


class VTKVisualizer:
    """
    3D VTK volumetric visualization and rendering engine
    
    Features:
    - DICOM to VTK volume conversion
    - Volume rendering with medical imaging windowing/leveling
    - Optional surface rendering (marching cubes)
    - Interactive camera control
    - Gesture control hooks
    """
    
    def __init__(self, window_title="HoloMed 3D Visualization"):
        """
        Initialize VTK visualization engine
        
        Args:
            window_title (str): Title for the rendering window
        """
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetWindowName(window_title)
        self.render_window.SetSize(1024, 768)
        
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.1, 0.1, 0.15)  # Dark blue background
        self.render_window.AddRenderer(self.renderer)
        
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        
        # Volume mapper and actor
        self.volume_mapper = None
        self.volume_actor = None
        
        # Actors for reference
        self.actors = []
        
    def create_volume_from_dicom(self, dicom_loader, use_surface_rendering=False):
        """
        Create 3D volumetric data from DICOM slices
        
        Args:
            dicom_loader (DICOMLoader): Loaded DICOM data
            use_surface_rendering (bool): Use marching cubes for surface vs volume rendering
            
        Returns:
            bool: Success status
        """
        try:
            if dicom_loader.file_count == 0:
                print("Error: No DICOM files loaded")
                return False
            
            # Stack all DICOM slices into 3D array
            volume_data = self._stack_dicom_slices(dicom_loader)
            if volume_data is None:
                return False
            
            print(f"Volume shape: {volume_data.shape}")
            
            if use_surface_rendering:
                success = self._render_surface(volume_data)
            else:
                success = self._render_volume(volume_data)
            
            if success:
                # Reset camera to show entire volume
                self.renderer.ResetCamera()
                self.renderer.GetActiveCamera().Zoom(1.5)
            
            return success
            
        except Exception as e:
            print(f"Error creating volume: {e}")
            return False
    
    def _stack_dicom_slices(self, dicom_loader):
        """
        Stack DICOM slices into a 3D volume
        
        Args:
            dicom_loader (DICOMLoader): Loaded DICOM data
            
        Returns:
            numpy.ndarray: 3D volume array (z, y, x)
        """
        try:
            slices = []
            
            # Extract pixel arrays from each DICOM file
            for i in range(dicom_loader.file_count):
                pixel_array = dicom_loader.get_pixel_array(i)
                if pixel_array is not None:
                    # Handle different slice dimensions
                    if pixel_array.ndim == 2:
                        slices.append(pixel_array)
                    elif pixel_array.ndim == 3:
                        # If 3D, take the first frame or average
                        slices.append(pixel_array[0])
                    elif pixel_array.ndim > 3:
                        # Flatten to 2D
                        slices.append(pixel_array.reshape(pixel_array.shape[-2:]))
            
            if not slices:
                print("Error: Could not extract pixel data from DICOM files")
                return None
            
            # Normalize all slices to a common shape
            target_shape = slices[0].shape
            normalized_slices = []
            
            for slice_data in slices:
                if slice_data.shape != target_shape:
                    # Resize to match target shape
                    from scipy import ndimage
                    zoom_factors = tuple(t / s for t, s in zip(target_shape, slice_data.shape))
                    resized = ndimage.zoom(slice_data, zoom_factors, order=1)
                    normalized_slices.append(resized)
                else:
                    normalized_slices.append(slice_data)
            
            # Stack slices along z-axis
            volume = np.array(normalized_slices, dtype=np.float32)
            
            print(f"Volume shape: {volume.shape}")
            
            # Normalize to 0-255 range for visualization
            volume_min = volume.min()
            volume_max = volume.max()
            
            if volume_max > volume_min:
                volume = ((volume - volume_min) / (volume_max - volume_min)) * 255.0
            
            return volume
            
        except Exception as e:
            print(f"Error stacking DICOM slices: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _render_volume(self, volume_data):
        """
        Render volume using VTK volume rendering
        
        Args:
            volume_data (numpy.ndarray): 3D volume array
            
        Returns:
            bool: Success status
        """
        try:
            # Convert numpy array to VTK ImageData
            vtk_volume = self._numpy_to_vtk_image(volume_data)
            
            # Create volume mapper
            self.volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
            self.volume_mapper.SetInputData(vtk_volume)
            
            # Create transfer function for opacity
            opacity_func = vtk.vtkPiecewiseFunction()
            opacity_func.AddPoint(0, 0.0)
            opacity_func.AddPoint(50, 0.2)
            opacity_func.AddPoint(128, 0.6)
            opacity_func.AddPoint(200, 0.9)
            opacity_func.AddPoint(255, 1.0)
            
            # Create color transfer function
            color_func = vtk.vtkColorTransferFunction()
            color_func.AddRGBPoint(0, 0.0, 0.0, 0.0)      # Black for low values
            color_func.AddRGBPoint(100, 0.2, 0.4, 0.8)    # Blue
            color_func.AddRGBPoint(150, 0.8, 0.4, 0.2)    # Orange
            color_func.AddRGBPoint(200, 1.0, 0.8, 0.0)    # Yellow
            color_func.AddRGBPoint(255, 1.0, 1.0, 1.0)    # White
            
            # Create volume property
            volume_property = vtk.vtkVolumeProperty()
            volume_property.SetColor(color_func)
            volume_property.SetScalarOpacity(opacity_func)
            volume_property.ShadeOn()
            volume_property.SetAmbient(0.4)
            volume_property.SetDiffuse(0.6)
            volume_property.SetSpecular(0.8)
            
            # Create volume actor
            self.volume_actor = vtk.vtkVolume()
            self.volume_actor.SetMapper(self.volume_mapper)
            self.volume_actor.SetProperty(volume_property)
            
            self.renderer.AddViewProp(self.volume_actor)
            self.actors.append(self.volume_actor)
            
            print("✓ Volume rendering initialized")
            return True
            
        except Exception as e:
            print(f"Error in volume rendering: {e}")
            return False
    
    def _render_surface(self, volume_data):
        """
        Render surface using marching cubes algorithm
        
        Args:
            volume_data (numpy.ndarray): 3D volume array
            
        Returns:
            bool: Success status
        """
        try:
            # Convert to VTK volume
            vtk_volume = self._numpy_to_vtk_image(volume_data)
            
            # Apply marching cubes to extract surface
            contour = vtk.vtkMarchingCubes()
            contour.SetInputData(vtk_volume)
            # Use optimal threshold value (50% of max)
            contour.SetValue(0, volume_data.max() * 0.5)
            contour.Update()
            
            # Create mapper and actor
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(contour.GetOutputPort())
            
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(0.8, 0.5, 0.3)  # Organ color
            actor.GetProperty().EdgeVisibilityOff()
            
            # Add smooth shading
            actor.GetProperty().SetSpecular(0.6)
            actor.GetProperty().SetSpecularPower(20)
            
            self.renderer.AddViewProp(actor)
            self.actors.append(actor)
            
            print("✓ Surface rendering (marching cubes) initialized")
            return True
            
        except Exception as e:
            print(f"Error in surface rendering: {e}")
            return False
    
    def _numpy_to_vtk_image(self, numpy_array):
        """
        Convert numpy 3D array to VTK ImageData
        
        Args:
            numpy_array (numpy.ndarray): 3D array (z, y, x)
            
        Returns:
            vtk.vtkImageData: VTK volume
        """
        # Ensure float32
        numpy_array = numpy_array.astype(np.float32)
        
        # Transpose to match VTK expectations (x, y, z)
        numpy_array = np.transpose(numpy_array, (2, 1, 0))
        
        # Convert to VTK array
        vtk_array = numpy_support.numpy_to_vtk(
            num_array=numpy_array.ravel(),
            deep=True,
            array_type=vtk.VTK_FLOAT
        )
        
        # Create ImageData
        image_data = vtk.vtkImageData()
        image_data.SetDimensions(numpy_array.shape[0], numpy_array.shape[1], numpy_array.shape[2])
        image_data.GetPointData().SetScalars(vtk_array)
        
        # Set spacing (1.0 for equal aspect ratio)
        image_data.SetSpacing(1.0, 1.0, 1.0)
        
        return image_data
    
    def set_windowing(self, window_center=50, window_width=400):
        """
        Set medical imaging window/level (similar to DICOM windowing)
        
        Args:
            window_center (int): Window center value
            window_width (int): Window width value
        """
        if self.volume_actor is None:
            return
        
        # Map window/level to opacity function
        window_min = window_center - window_width / 2
        window_max = window_center + window_width / 2
        
        opacity_func = vtk.vtkPiecewiseFunction()
        opacity_func.AddPoint(window_min, 0.0)
        opacity_func.AddPoint(window_center, 0.6)
        opacity_func.AddPoint(window_max, 1.0)
        
        self.volume_actor.GetProperty().SetScalarOpacity(opacity_func)
    
    def rotate_model(self, rx, ry, rz):
        """
        Rotate the 3D model
        
        Args:
            rx (float): Rotation around X-axis (degrees)
            ry (float): Rotation around Y-axis (degrees)
            rz (float): Rotation around Z-axis (degrees)
        """
        if self.volume_actor is None:
            return
        
        current_matrix = self.volume_actor.GetUserMatrix()
        if current_matrix is None:
            matrix = vtk.vtkMatrix4x4()
        else:
            matrix = vtk.vtkMatrix4x4()
            matrix.DeepCopy(current_matrix)
        
        # Create rotation matrix
        transform = vtk.vtkTransform()
        transform.SetMatrix(matrix)
        transform.RotateX(rx)
        transform.RotateY(ry)
        transform.RotateZ(rz)
        
        self.volume_actor.SetUserMatrix(transform.GetMatrix())
    
    def translate_model(self, tx, ty, tz):
        """
        Translate the 3D model
        
        Args:
            tx (float): Translation along X-axis
            ty (float): Translation along Y-axis
            tz (float): Translation along Z-axis
        """
        if self.volume_actor is None:
            return
        
        current_matrix = self.volume_actor.GetUserMatrix()
        if current_matrix is None:
            matrix = vtk.vtkMatrix4x4()
        else:
            matrix = vtk.vtkMatrix4x4()
            matrix.DeepCopy(current_matrix)
        
        transform = vtk.vtkTransform()
        transform.SetMatrix(matrix)
        transform.Translate(tx, ty, tz)
        
        self.volume_actor.SetUserMatrix(transform.GetMatrix())
    
    def scale_model(self, sx, sy, sz):
        """
        Scale the 3D model
        
        Args:
            sx (float): Scale factor X
            sy (float): Scale factor Y
            sz (float): Scale factor Z
        """
        if self.volume_actor is None:
            return
        
        current_matrix = self.volume_actor.GetUserMatrix()
        if current_matrix is None:
            matrix = vtk.vtkMatrix4x4()
        else:
            matrix = vtk.vtkMatrix4x4()
            matrix.DeepCopy(current_matrix)
        
        transform = vtk.vtkTransform()
        transform.SetMatrix(matrix)
        transform.Scale(sx, sy, sz)
        
        self.volume_actor.SetUserMatrix(transform.GetMatrix())
    
    def show(self):
        """Display the visualization window"""
        try:
            if self.volume_actor is None:
                print("Warning: No volume loaded. Load DICOM data first.")
                return
            
            print("\n" + "="*50)
            print("Starting VTK Visualization")
            print("="*50)
            print("Controls:")
            print("  - Left click + drag: Rotate")
            print("  - Right click + drag: Zoom")
            print("  - Middle click + drag: Pan")
            print("  - 'Q' or close window: Exit")
            print("="*50 + "\n")
            
            self.interactor.Initialize()
            self.render_window.Render()
            self.interactor.Start()
            
        except Exception as e:
            print(f"Error starting visualization: {e}")
    
    def get_camera(self):
        """Get the active camera"""
        return self.renderer.GetActiveCamera()
    
    def reset_camera(self):
        """Reset camera to default position"""
        self.renderer.ResetCamera()
        self.renderer.GetActiveCamera().Zoom(1.5)


# Example usage
if __name__ == "__main__":
    from dicom_loader import DICOMLoader
    import sys
    
    # Load DICOM data
    loader = DICOMLoader()
    loader.load_folder(".")
    
    if loader.file_count > 0:
        # Create visualizer
        viz = VTKVisualizer()
        
        # Check command line arguments for rendering mode
        render_mode = "volume"  # default
        if len(sys.argv) > 1:
            if sys.argv[1] == "--skull":
                render_mode = "skull"
            elif sys.argv[1] == "--heart":
                render_mode = "heart"
            elif sys.argv[1] == "--surface":
                render_mode = "surface"
        
        print(f"\n{'='*50}")
        print(f"Rendering Mode: {render_mode.upper()}")
        print(f"{'='*50}")
        
        if render_mode == "skull":
            # Create volume from DICOM with surface rendering (good for bones/skull)
            print("Displaying SKULL (Bone Window - High Threshold)")
            if viz.create_volume_from_dicom(loader, use_surface_rendering=True):
                # Adjust windowing for bone/skull visualization
                viz.set_windowing(window_center=400, window_width=1600)  # Bone window
                viz.show()
        elif render_mode == "heart":
            # Create volume from DICOM with volume rendering (good for soft tissue)
            print("Displaying HEART (Soft Tissue Window)")
            if viz.create_volume_from_dicom(loader, use_surface_rendering=False):
                # Adjust windowing for soft tissue/heart visualization
                viz.set_windowing(window_center=50, window_width=350)  # Soft tissue window
                viz.show()
        elif render_mode == "surface":
            print("Displaying SURFACE (3D Surface Extraction)")
            if viz.create_volume_from_dicom(loader, use_surface_rendering=True):
                viz.show()
        else:  # volume
            print("Displaying VOLUME (Full 3D Volume Rendering)")
            if viz.create_volume_from_dicom(loader, use_surface_rendering=False):
                viz.show()
    else:
        print("No DICOM files found")
