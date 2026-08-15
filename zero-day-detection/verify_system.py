"""
System Verification Script
Checks if all components are properly installed and configured
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking dependencies...")
    required = [
        'numpy', 'pandas', 'scikit-learn', 'xgboost', 
        'tensorflow', 'keras', 'shap', 'streamlit', 
        'plotly', 'yaml', 'joblib'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (not installed)")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_directories():
    """Check if required directories exist"""
    print("\n📁 Checking directories...")
    directories = ['src', 'config', 'models', 'data']
    
    all_exist = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/")
        else:
            print(f"   ❌ {directory}/ (missing)")
            all_exist = False
    
    return all_exist

def check_config():
    """Check if configuration file exists"""
    print("\n⚙️  Checking configuration...")
    config_path = 'config/detection_config.yaml'
    
    if os.path.exists(config_path):
        print(f"   ✅ {config_path}")
        return True
    else:
        print(f"   ❌ {config_path} (missing)")
        return False

def check_models():
    """Check if trained models exist"""
    print("\n🤖 Checking trained models...")
    model_files = [
        'models/isolation_forest.joblib',
        'models/autoencoder.h5',
        'models/random_forest.joblib',
        'models/xgboost.joblib',
        'models/scaler.joblib',
        'models/encoder.joblib'
    ]
    
    found = 0
    for model_file in model_files:
        if os.path.exists(model_file):
            size = os.path.getsize(model_file) / 1024  # KB
            print(f"   ✅ {model_file} ({size:.1f} KB)")
            found += 1
        else:
            print(f"   ⚠️  {model_file} (not found)")
    
    return found > 0, found, len(model_files)

def check_source_files():
    """Check if source files exist"""
    print("\n📄 Checking source files...")
    source_files = [
        'app.py',
        'train_models.py',
        'src/feature_extractor.py',
        'src/anomaly_detector.py',
        'src/attack_classifier.py',
        'src/ensemble_voter.py',
        'src/explainability_engine.py',
        'src/detection_system.py',
        'src/data_generator.py'
    ]
    
    all_exist = True
    for source_file in source_files:
        if os.path.exists(source_file):
            print(f"   ✅ {source_file}")
        else:
            print(f"   ❌ {source_file} (missing)")
            all_exist = False
    
    return all_exist

def test_imports():
    """Test if modules can be imported"""
    print("\n🔍 Testing module imports...")
    
    sys.path.insert(0, 'src')
    
    modules = [
        'feature_extractor',
        'anomaly_detector',
        'attack_classifier',
        'ensemble_voter',
        'explainability_engine',
        'detection_system',
        'data_generator'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except Exception as e:
            print(f"   ❌ {module} ({str(e)[:50]}...)")
            all_ok = False
    
    return all_ok

def main():
    """Main verification function"""
    print("="*60)
    print("Zero-Day Network Attack Detection System")
    print("System Verification")
    print("="*60)
    
    checks = []
    
    # Run all checks
    checks.append(("Python Version", check_python_version()))
    
    deps_ok, missing = check_dependencies()
    checks.append(("Dependencies", deps_ok))
    
    checks.append(("Directories", check_directories()))
    checks.append(("Configuration", check_config()))
    
    models_exist, found, total = check_models()
    checks.append(("Models", models_exist))
    
    checks.append(("Source Files", check_source_files()))
    checks.append(("Module Imports", test_imports()))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:.<40} {status}")
    
    passed = sum(1 for _, result in checks if result)
    total_checks = len(checks)
    
    print(f"\nPassed: {passed}/{total_checks}")
    
    if found < total:
        print(f"\nModels: {found}/{total} found")
        if found == 0:
            print("\n⚠️  No models found. Run: python train_models.py")
    
    if not deps_ok:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
    
    print("\n" + "="*60)
    
    if passed == total_checks and found == total:
        print("✅ System is ready! Run: streamlit run app.py")
    elif passed >= total_checks - 1 and models_exist:
        print("⚠️  System partially ready. Some components missing.")
    else:
        print("❌ System not ready. Please fix the issues above.")
    
    print("="*60)
    
    return passed == total_checks

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
