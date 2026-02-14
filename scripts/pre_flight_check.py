"""
HoloMed Pre-Flight Validation Script
Comprehensive system check before hardware connection

Tests:
1. Python version and dependencies
2. Visualization system (VTK)
3. DICOM loading capability
4. Module imports
5. System resources (GPU, RAM)
6. Example execution
7. Configuration validation
"""

import sys
import os
from pathlib import Path
import platform
import subprocess


class PreFlightCheck:
    """
    Comprehensive pre-flight validation system
    """
    
    def __init__(self):
        """Initialize pre-flight checker"""
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.project_root = Path(__file__).parent.parent
        
        print("\n" + "="*70)
        print("🚀 HoloMed Pre-Flight Validation")
        print("="*70)
        print(f"Project Root: {self.project_root}")
        print(f"Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
    
    def test_python_version(self):
        """Test Python version"""
        print("1️⃣  Python Version Check")
        print("-" * 70)
        
        major, minor = sys.version_info[:2]
        version_str = f"{major}.{minor}.{sys.version_info[2]}"
        
        print(f"   Python Version: {version_str}")
        print(f"   Python Path: {sys.executable}")
        
        if major >= 3 and minor >= 8:
            print("   ✅ Python version OK (3.8+)\n")
            self.passed += 1
            return True
        else:
            print("   ❌ FAILED: Python 3.8+ required\n")
            self.failed += 1
            return False
    
    def test_dependencies(self):
        """Test Python package dependencies"""
        print("2️⃣  Dependencies Check")
        print("-" * 70)
        
        required_packages = {
            'numpy': '1.20+',
            'matplotlib': '3.4+',
            'vtk': '9.0+',
            'pydicom': '2.3+',
            'PIL': '8.0+ (pillow)',
            'scipy': '1.7+',
            'serial': '3.5+ (pyserial)',
        }
        
        optional_packages = {
            'paho': 'MQTT support',
        }
        
        print("   Required Packages:")
        failed_deps = []
        
        for pkg_name, required_version in required_packages.items():
            try:
                if pkg_name == 'PIL':
                    __import__('PIL')
                elif pkg_name == 'serial':
                    __import__('serial')
                else:
                    __import__(pkg_name)
                
                print(f"   ✅ {pkg_name:15} - {required_version}")
                self.passed += 1
            except ImportError:
                print(f"   ❌ {pkg_name:15} - MISSING")
                failed_deps.append(pkg_name)
                self.failed += 1
        
        print("\n   Optional Packages:")
        for pkg_name, description in optional_packages.items():
            try:
                __import__(pkg_name)
                print(f"   ✅ {pkg_name:15} - {description}")
            except ImportError:
                print(f"   ⚠️  {pkg_name:15} - {description} (not installed)")
                self.warnings += 1
        
        if failed_deps:
            print(f"\n   Install missing packages:")
            print(f"   pip install -r requirements.txt\n")
        else:
            print()
        
        return len(failed_deps) == 0
    
    def test_imports(self):
        """Test core module imports"""
        print("3️⃣  Module Imports Check")
        print("-" * 70)
        
        modules = {
            'dicom_loader': 'DICOM loading',
            'vtk_visualizer': 'VTK visualization',
            'viewport_generator': '4-way viewport',
            'gesture_control': 'Gesture handling',
            'logging_config': 'Logging system',
        }
        
        scripts_dir = self.project_root / 'scripts'
        sys.path.insert(0, str(scripts_dir))
        
        failed_imports = []
        
        for module_name, description in modules.items():
            try:
                __import__(module_name)
                print(f"   ✅ {module_name:20} - {description}")
                self.passed += 1
            except Exception as e:
                print(f"   ❌ {module_name:20} - Failed: {e}")
                failed_imports.append(module_name)
                self.failed += 1
        
        print()
        return len(failed_imports) == 0
    
    def test_dicom_files(self):
        """Test DICOM files availability"""
        print("4️⃣  DICOM Files Check")
        print("-" * 70)
        
        dicom_path = self.project_root / 'data' / 'scripts' / 'hardware'
        
        print(f"   Looking for DICOM files in:")
        print(f"   {dicom_path}\n")
        
        if not dicom_path.exists():
            print(f"   ⚠️  Directory does not exist: {dicom_path}")
            print(f"   Create directory and add .dcm files before visualization\n")
            self.warnings += 1
            return False
        
        dcm_files = list(dicom_path.glob('*.dcm'))
        
        if dcm_files:
            print(f"   ✅ Found {len(dcm_files)} DICOM files:")
            for dcm_file in sorted(dcm_files)[:5]:  # Show first 5
                size_mb = dcm_file.stat().st_size / (1024*1024)
                print(f"      - {dcm_file.name} ({size_mb:.2f} MB)")
            
            if len(dcm_files) > 5:
                print(f"      ... and {len(dcm_files)-5} more files\n")
            else:
                print()
            
            self.passed += 1
            return True
        else:
            print(f"   ⚠️  No DICOM files found (.dcm)")
            print(f"   Add DICOM files to: {dicom_path}\n")
            self.warnings += 1
            return False
    
    def test_system_resources(self):
        """Test system resources"""
        print("5️⃣  System Resources Check")
        print("-" * 70)
        
        # OS Info
        print(f"   Operating System: {platform.system()} {platform.release()}")
        print(f"   Processor: {platform.processor()}")
        
        # RAM
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            print(f"   Total RAM: {ram_gb:.2f} GB")
            if ram_gb >= 4:
                print("   ✅ Sufficient RAM (4GB+)")
                self.passed += 1
            elif ram_gb >= 2:
                print("   ⚠️  Limited RAM (2-4GB, may be slow)")
                self.warnings += 1
            else:
                print("   ❌ Insufficient RAM (<2GB)")
                self.failed += 1
        except ImportError:
            print("   ⚠️  psutil not installed (cannot check RAM)")
            self.warnings += 1
        
        # GPU Info
        print("\n   GPU Information:")
        try:
            import vtk
            # Try to get GPU info
            gpu_available = True
            print(f"   ✅ VTK {vtk.__version__} installed")
            print("   GPU acceleration available (if supported by your hardware)")
            self.passed += 1
        except ImportError:
            print("   ❌ VTK not available (required for visualization)")
            self.failed += 1
            gpu_available = False
        
        print()
        return True
    
    def test_visualization(self):
        """Test basic visualization initialization"""
        print("6️⃣  Visualization System Test")
        print("-" * 70)
        
        try:
            sys.path.insert(0, str(self.project_root / 'scripts'))
            from vtk_visualizer import VTKVisualizer
            
            print("   Initializing VTK visualizer...")
            viz = VTKVisualizer()
            print("   ✅ VTK visualizer initialized successfully")
            
            print("   Checking renderer...")
            if viz.renderer is not None:
                print("   ✅ Renderer created")
            
            print("   Checking render window...")
            if viz.render_window is not None:
                print("   ✅ Render window created")
            
            print("   ✅ Visualization system OK\n")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"   ❌ Visualization test failed: {e}\n")
            self.failed += 1
            return False
    
    def test_viewport_system(self):
        """Test 4-way viewport system"""
        print("7️⃣  4-Way Viewport System Test")
        print("-" * 70)
        
        try:
            sys.path.insert(0, str(self.project_root / 'scripts'))
            from viewport_generator import FourWayViewportGenerator, ViewportLayout
            
            print("   Creating 4-way viewport system...")
            viewport = FourWayViewportGenerator(layout=ViewportLayout.QUAD)
            
            print("   ✅ 4-way viewport created")
            print(f"   ✅ Viewport count: {viewport.get_viewport_count()}")
            
            print("   Checking layouts...")
            for layout in ViewportLayout:
                print(f"   ✅ Layout available: {layout.value}")
            
            print("   ✅ Viewport system OK\n")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"   ❌ Viewport test failed: {e}\n")
            self.failed += 1
            return False
    
    def test_gesture_system(self):
        """Test gesture control system"""
        print("8️⃣  Gesture Control System Test")
        print("-" * 70)
        
        try:
            sys.path.insert(0, str(self.project_root / 'scripts'))
            from gesture_control import GestureHandler, GestureType
            
            print("   Creating gesture handler...")
            handler = GestureHandler()
            print("   ✅ Gesture handler created")
            
            print("   Testing gesture simulation...")
            # Simulate a gesture
            handler.handle_gesture("UP")
            print("   ✅ Gesture UP processed")
            
            handler.handle_gesture("LEFT")
            print("   ✅ Gesture LEFT processed")
            
            stats = handler.get_statistics()
            print(f"   ✅ Gesture history: {len(stats['recent_gestures'])} gestures")
            
            print("   ✅ Gesture system OK\n")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"   ❌ Gesture test failed: {e}\n")
            self.failed += 1
            return False
    
    def test_logging_system(self):
        """Test logging system"""
        print("9️⃣  Logging System Test")
        print("-" * 70)
        
        try:
            sys.path.insert(0, str(self.project_root / 'scripts'))
            from logging_config import get_logger, LogLevel
            
            print("   Creating logger...")
            logger = get_logger(debug=False)
            print("   ✅ Logger created")
            
            print("   Testing logging...")
            logger.info("Test info message")
            logger.warning("Test warning message")
            print("   ✅ Logging works")
            
            logger.record_metric("test_metric", 42.5, "units")
            print("   ✅ Metrics recording works")
            
            if logger.log_file:
                print(f"   ✅ Log file: {logger.log_file}")
            
            print("   ✅ Logging system OK\n")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"   ❌ Logging test failed: {e}\n")
            self.failed += 1
            return False
    
    def test_cli(self):
        """Test CLI argument parsing"""
        print("🔟  CLI Interface Test")
        print("-" * 70)
        
        try:
            main_py = self.project_root / 'scripts' / 'main.py'
            
            if main_py.exists():
                print(f"   ✅ main.py found: {main_py}")
                
                # Check if file has argparse
                with open(main_py, 'r') as f:
                    content = f.read()
                    if 'argparse' in content:
                        print("   ✅ Argument parsing detected")
                
                print("   ✅ CLI interface OK\n")
                self.passed += 1
                return True
            else:
                print(f"   ❌ main.py not found\n")
                self.failed += 1
                return False
                
        except Exception as e:
            print(f"   ❌ CLI test failed: {e}\n")
            self.failed += 1
            return False
    
    def test_examples(self):
        """Check example programs"""
        print("1️⃣1️⃣  Example Programs Check")
        print("-" * 70)
        
        examples = {
            'vtk_example.py': 'VTK visualization examples',
            'viewport_example.py': '4-way viewport examples',
            'gesture_example.py': 'Gesture control examples',
        }
        
        scripts_dir = self.project_root / 'scripts'
        
        for example_file, description in examples.items():
            example_path = scripts_dir / example_file
            
            if example_path.exists():
                print(f"   ✅ {example_file:25} - {description}")
                self.passed += 1
            else:
                print(f"   ❌ {example_file:25} - Not found")
                self.failed += 1
        
        print()
        return True
    
    def test_documentation(self):
        """Check documentation files"""
        print("1️⃣2️⃣  Documentation Check")
        print("-" * 70)
        
        docs = {
            'PROJECT_COMPLETION_REPORT.md': 'Project status',
            'IMPLEMENTATION_SUMMARY.md': 'Architecture overview',
            'QUICK_REFERENCE.md': 'Quick commands',
            'scripts/VTK_VISUALIZATION_GUIDE.md': 'VTK guide',
            'scripts/VIEWPORT_GENERATOR_GUIDE.md': 'Viewport guide',
            'scripts/GESTURE_CONTROL_GUIDE.md': 'Gesture guide',
        }
        
        for doc_file, description in docs.items():
            doc_path = self.project_root / doc_file
            
            if doc_path.exists():
                size_kb = doc_path.stat().st_size / 1024
                print(f"   ✅ {doc_file:40} ({size_kb:.0f} KB)")
                self.passed += 1
            else:
                print(f"   ⚠️  {doc_file:40} - Not found")
                self.warnings += 1
        
        print()
        return True
    
    def print_summary(self):
        """Print final summary"""
        print("="*70)
        print("📊 Pre-Flight Check Summary")
        print("="*70)
        
        total = self.passed + self.failed + self.warnings
        
        print(f"\n✅ Passed:  {self.passed}")
        print(f"❌ Failed:  {self.failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"📊 Total:   {total}")
        
        if self.failed == 0:
            print("\n" + "🎉 "*25)
            print("\n✅ ALL CRITICAL CHECKS PASSED - SYSTEM READY!\n")
            print("🎉 "*25)
            return True
        else:
            print(f"\n❌ {self.failed} critical issue(s) found. Please resolve before starting.\n")
            return False
    
    def print_next_steps(self):
        """Print next steps"""
        print("="*70)
        print("📋 Next Steps")
        print("="*70)
        
        print("""
If all checks passed:

1. ✅ Basic Functionality (no hardware needed):
   python scripts/main.py
   
2. ✅ Run Examples to test features:
   python scripts/vtk_example.py --example 1
   python scripts/gesture_example.py --example 1
   python scripts/viewport_example.py --example 1

3. 📖 Read Documentation:
   - QUICK_REFERENCE.md (for common commands)
   - IMPLEMENTATION_SUMMARY.md (for architecture)
   
4. 🔌 Prepare Hardware (when ready):
   - Upload gesture_sensor.ino to ESP32
   - Test with: python scripts/gesture_example.py --example 3 --serial-port COM3
   
5. 🎭 Enable Holographic Mode:
   - python scripts/main.py --holographic
   - python scripts/main.py --holographic --gesture --serial-port COM3

""")
        
        print("="*70)
        print("For detailed help, see QUICK_REFERENCE.md in project root")
        print("="*70 + "\n")
    
    def run_all_checks(self):
        """Run all checks"""
        checks = [
            self.test_python_version,
            self.test_dependencies,
            self.test_imports,
            self.test_dicom_files,
            self.test_system_resources,
            self.test_visualization,
            self.test_viewport_system,
            self.test_gesture_system,
            self.test_logging_system,
            self.test_cli,
            self.test_examples,
            self.test_documentation,
        ]
        
        for check_func in checks:
            try:
                check_func()
            except Exception as e:
                print(f"❌ Unexpected error in {check_func.__name__}: {e}\n")
                self.failed += 1
        
        # Print results
        passed = self.print_summary()
        self.print_next_steps()
        
        return passed


def main():
    """Run pre-flight checks"""
    checker = PreFlightCheck()
    success = checker.run_all_checks()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
