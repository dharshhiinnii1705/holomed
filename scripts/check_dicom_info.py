import pydicom
from pathlib import Path

# Check first 5 DICOM files for metadata
dcm_files = sorted(Path('.').glob('image-*.dcm'))[:5]

print('DICOM File Information:')
print('='*60)

for dcm_file in dcm_files:
    try:
        ds = pydicom.dcmread(str(dcm_file))
        print(f'\nFile: {dcm_file.name}')
        print(f'  Modality: {ds.Modality if hasattr(ds, "Modality") else "Unknown"}')
        print(f'  Body Part: {ds.BodyPartExamined if hasattr(ds, "BodyPartExamined") else "Unknown"}')
        print(f'  Patient Name: {ds.PatientName if hasattr(ds, "PatientName") else "Unknown"}')
        print(f'  Study Description: {ds.StudyDescription if hasattr(ds, "StudyDescription") else "Unknown"}')
        print(f'  Series Description: {ds.SeriesDescription if hasattr(ds, "SeriesDescription") else "Unknown"}')
        print(f'  Image Type: {ds.ImageType if hasattr(ds, "ImageType") else "Unknown"}')
        print(f'  Dimensions: {ds.Rows} x {ds.Columns} if hasattr(ds, "Rows") else "Unknown"')
    except Exception as e:
        print(f'{dcm_file.name}: Error - {e}')

print('\n' + '='*60)
print(f'Total DICOM files found: {len(sorted(Path(".").glob("*.dcm")))}')
