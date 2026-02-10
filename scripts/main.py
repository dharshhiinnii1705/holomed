"""
HoloMed - Main Application
Combines VTK visualization with gesture control from ESP32 sensor
"""

import sys
import os
from dicom_loader import DICOMLoader


def main():
    print("HoloMed - Medical Imaging with Gesture Control")
    print("=" * 50)
    
    # Initialize DICOM loader
    loader = DICOMLoader()
    
    # Load DICOM files from data folder
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "scripts", "hardware")
    files = loader.load_folder(data_path)
    
    if loader.file_count > 0:
        print(f"\nSuccessfully loaded {loader.file_count} DICOM files")
        
        # Display info about first file
        info = loader.get_info(0)
        print("\nFirst file information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    # TODO: Add VTK initialization and visualization
    # TODO: Add gesture sensor integration


if __name__ == "__main__":
    main()
