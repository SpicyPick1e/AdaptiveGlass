import PyInstaller.__main__
import os
import shutil
import sys

# Define paths
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, "adaptive_glass")
main_script = os.path.join(src_dir, "main.py")
resources_dir = os.path.join(src_dir, "resources")
dist_dir = os.path.join(base_dir, "dist")
build_dir = os.path.join(base_dir, "build")

# Clean previous builds
print("Cleaning previous builds...")
if os.path.exists(dist_dir):
    shutil.rmtree(dist_dir)
if os.path.exists(build_dir):
    shutil.rmtree(build_dir)

# Ensure resources exist
if not os.path.exists(resources_dir):
    print(f"Error: Resources directory not found at {resources_dir}")
    # Create it if it doesn't exist to prevent build failure, though app might need it
    os.makedirs(resources_dir, exist_ok=True)

# PyInstaller arguments
args = [
    main_script,
    '--name=AdaptiveGlass_V1.0',
    '--onefile', # Single executable
    '--windowed', # No console window
    '--noconfirm',
    f'--add-data={resources_dir}{os.pathsep}resources', # Bundle resources
    '--clean',
    
    # Exclude unnecessary modules to reduce size
    '--exclude-module=tkinter',
    '--exclude-module=unittest',
    '--exclude-module=email',
    '--exclude-module=http',
    '--exclude-module=xml',
    '--exclude-module=pydoc',
    '--exclude-module=pdb',
    '--exclude-module=distutils',
    '--exclude-module=setuptools',
    # '--exclude-module=numpy', # Numpy might be needed by PIL or OpenCV, keep it for safety unless sure
    
    # Hidden imports (explicitly include these if PyInstaller misses them)
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageDraw',
    '--hidden-import=PIL.ImageFont',
    '--hidden-import=PIL.ImageFilter',
    '--hidden-import=piexif',
    '--hidden-import=PyQt6',
    f'--icon={os.path.join(resources_dir, "logos", "applogo.ico")}',
]

print("Starting build process...")
print(f"Target: {main_script}")
print(f"Resources: {resources_dir}")

try:
    PyInstaller.__main__.run(args)
    print(f"\nBuild complete successfully!")
    exe_path = os.path.join(dist_dir, 'AdaptiveGlass_V1.0.exe')
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"Executable is located at: {exe_path}")
        print(f"Size: {size_mb:.2f} MB")
    else:
        print("Error: Executable not found after build.")
except Exception as e:
    print(f"\nBuild failed: {e}")
