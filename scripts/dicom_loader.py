"""
DICOM Loader Module
Handles loading and processing DICOM medical imaging files
"""

import os
import pydicom
import numpy as np
from pathlib import Path


class DICOMLoader:
    """Load and process DICOM files"""
    
    def __init__(self, folder_path=None):
        """
        Initialize DICOM loader
        
        Args:
            folder_path (str): Path to folder containing DICOM files
        """
        self.folder_path = folder_path
        self.dicom_files = []
        self.dataset = None
        
    def load_folder(self, folder_path):
        """
        Load all DICOM files from a folder
        
        Args:
            folder_path (str): Path to folder with DICOM files
            
        Returns:
            list: List of loaded DICOM datasets
        """
        self.folder_path = folder_path
        self.dicom_files = []
        
        if not os.path.exists(folder_path):
            print(f"Error: Folder '{folder_path}' not found")
            return []
        
        # Find all .dcm files
        dcm_files = list(Path(folder_path).glob("*.dcm"))
        
        if not dcm_files:
            print(f"No DICOM files found in {folder_path}")
            return []
        
        print(f"Found {len(dcm_files)} DICOM files")
        
        # Load each DICOM file
        for dcm_file in sorted(dcm_files):
            try:
                ds = pydicom.dcmread(str(dcm_file))
                self.dicom_files.append({
                    'path': str(dcm_file),
                    'dataset': ds,
                    'filename': dcm_file.name
                })
            except Exception as e:
                print(f"Error loading {dcm_file.name}: {e}")
        
        print(f"Successfully loaded {len(self.dicom_files)} files")
        return self.dicom_files
    
    def get_pixel_array(self, index=0):
        """
        Get pixel array from a specific DICOM file
        
        Args:
            index (int): Index of DICOM file in loaded list
            
        Returns:
            numpy.ndarray: Pixel data as numpy array
        """
        if index >= len(self.dicom_files):
            print(f"Error: Index {index} out of range")
            return None
        
        try:
            ds = self.dicom_files[index]['dataset']
            return ds.pixel_array
        except Exception as e:
            print(f"Error getting pixel array: {e}")
            return None
    
    def get_info(self, index=0):
        """
        Get metadata from DICOM file
        
        Args:
            index (int): Index of DICOM file
            
        Returns:
            dict: Dictionary with DICOM metadata
        """
        if index >= len(self.dicom_files):
            return None
        
        ds = self.dicom_files[index]['dataset']
        info = {
            'filename': self.dicom_files[index]['filename'],
            'rows': int(ds.Rows) if 'Rows' in ds else None,
            'columns': int(ds.Columns) if 'Columns' in ds else None,
            'modality': ds.Modality if 'Modality' in ds else 'Unknown',
            'patient_name': ds.PatientName if 'PatientName' in ds else 'Unknown',
            'patient_id': ds.PatientID if 'PatientID' in ds else 'Unknown'
        }
        return info
    
    def list_files(self):
        """
        List all loaded DICOM files
        
        Returns:
            list: List of filenames
        """
        return [f['filename'] for f in self.dicom_files]

    @property
    def file_count(self):
        """Get number of loaded DICOM files"""
        return len(self.dicom_files)


# Example usage
if __name__ == "__main__":
    loader = DICOMLoader()
    
    # Example: Load from data folder
    loader.load_folder("./data/scripts/hardware")
    
    # List files
    print("\nLoaded files:")
    for fname in loader.list_files():
        print(f"  - {fname}")
    
    # Get info from first file
    if loader.file_count > 0:
        info = loader.get_info(0)
        print(f"\nFirst file info: {info}")
