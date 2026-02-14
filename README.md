
# HoloMed 🏥
Medical Imaging Visualization with Gesture Control

## Project Overview
HoloMed combines VTK-based 3D medical imaging visualization with real-time gesture control via an ESP32 sensor.

## Folder Structure
```
HoloMed/
├── data/
│   └── scripts/
│       └── hardware/          # Hardware-specific documentation
├── scripts/
│   └── main.py               # Main VTK visualization application
├── hardware/
│   └── gesture_sensor.ino    # ESP32 gesture sensor firmware
└── requirements.txt          # Python dependencies
```

## Development Workflow

### 1. Before Starting a Session
```bash
git pull origin main
```

### 2. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

Examples:
- `feature/dicom-loader` - For DICOM file loading
- `feature/gesture-logic` - For gesture recognition
- `feature/vtk-rendering` - For 3D visualization

### 3. Develop & Save (Three-Step Process)
```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Add logic to read MRI slices"

# Push to GitHub
git push origin feature/your-feature-name
```

### 4. Create a Pull Request (on GitHub.com)
- Go to GitHub
- Click "Compare & pull request"
- Add description of what your feature does
- Request review from team members
- Once approved, merge into main

## Getting Started
1. Clone the repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Start coding on your branch
5. Follow the three-step save process
6. Create a PR when ready

## Team Members
- @dharshhiinnii1705

---
For questions or issues, create an issue on GitHub!
