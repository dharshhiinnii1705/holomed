import pydicom
import numpy as np
from pathlib import Path

# Check pixel data characteristics
dcm_files = sorted(Path('.').glob('image-*.dcm'))[:10]

print('DICOM Pixel Data Analysis:')
print('='*60)

pixel_values = []

for dcm_file in dcm_files:
    try:
        ds = pydicom.dcmread(str(dcm_file))
        pixel_array = ds.pixel_array
        pixel_values.extend(pixel_array.flatten())
        
        if dcm_file == dcm_files[0]:
            print(f'\nFile: {dcm_file.name}')
            print(f'  Min Pixel Value: {pixel_array.min()}')
            print(f'  Max Pixel Value: {pixel_array.max()}')
            print(f'  Mean Pixel Value: {pixel_array.mean():.2f}')
            print(f'  Std Dev: {pixel_array.std():.2f}')
    except Exception as e:
        print(f'{dcm_file.name}: Error - {e}')

pixel_values = np.array(pixel_values)

print('\n' + '='*60)
print('Overall Statistics:')
print(f'  Global Min: {pixel_values.min()}')
print(f'  Global Max: {pixel_values.max()}')
print(f'  Global Mean: {pixel_values.mean():.2f}')
print(f'  Global Std Dev: {pixel_values.std():.2f}')

print('\n' + '='*60)
print('Organ Type Analysis:')

if pixel_values.max() > 2000:
    print('✓ LIKELY BONE/SKULL - High pixel values (CT HU > 400)')
    print('  Recommendation: Use --skull mode')
elif 200 < pixel_values.mean() < 500:
    print('✓ LIKELY MIXED TISSUE/ORGANS')
    print('  Recommendation: Use --heart mode or --surface mode')
elif pixel_values.max() < 500:
    print('✓ LIKELY SOFT TISSUE (Brain, Heart, Organs)')
    print('  Recommendation: Use --heart or --surface mode')
else:
    print('✓ GENERAL CT SCAN')
    print('  Recommendation: Try different modes to see')
