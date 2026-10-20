"""
Check & Install Dependencies for ML Lawyer Recommendation System
"""

import subprocess
import sys

# Required packages for model training
REQUIRED_PACKAGES = {
    'pandas': 'pandas',
    'numpy': 'numpy',
    'scikit-learn': 'sklearn',
    'pickle': 'Built-in Python module',
    'json': 'Built-in Python module',
}

RECOMMENDED_PACKAGES = {
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'streamlit': 'streamlit',
}


def check_and_install():
    """Check and install required packages"""
    
    print("=" * 70)
    print("  CHECKING DEPENDENCIES FOR ML LAWYER RECOMMENDATION SYSTEM  ")
    print("=" * 70)
    
    missing = []
    
    print("\n📋 Checking required packages...")
    for package_name, import_name in REQUIRED_PACKAGES.items():
        try:
            if import_name == 'Built-in Python module':
                print(f"  ✓ {package_name}")
            else:
                __import__(import_name)
                print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} - NOT FOUND")
            if import_name != 'Built-in Python module':
                missing.append(package_name)
    
    print("\n🔍 Checking recommended packages...")
    for package_name, import_name in RECOMMENDED_PACKAGES.items():
        try:
            __import__(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ⚠ {package_name} - optional (needed for full system)")
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} required package(s)")
        print("\nInstalling missing packages...")
        
        for package in missing:
            print(f"\n  Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
                print(f"  ✓ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"  ✗ Failed to install {package}")
                print(f"    Try manually: pip install {package}")
    
    print("\n" + "=" * 70)
    print("✓ DEPENDENCY CHECK COMPLETE")
    print("=" * 70)
    print("\n✅ Ready to run ML training scripts!")
    print("\nRun commands:")
    print("  cd D:\\legal\\backend")
    print("  python data_preparation.py")
    print("  python train_lawyer_model.py")


if __name__ == "__main__":
    check_and_install()
