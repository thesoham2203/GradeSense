#!/usr/bin/env python3
"""
Setup script for GradeSense API
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("Please upgrade to Python 3.9 or higher")
        return False

def install_system_dependencies():
    """Install system dependencies based on OS"""
    print_header("Installing System Dependencies")
    
    system = platform.system().lower()
    
    if system == "linux":
        # Ubuntu/Debian
        commands = [
            "sudo apt-get update",
            "sudo apt-get install -y tesseract-ocr tesseract-ocr-eng libgl1-mesa-glx libglib2.0-0"
        ]
        for cmd in commands:
            if not run_command(cmd, f"Running: {cmd}"):
                return False
    
    elif system == "darwin":  # macOS
        if not run_command("brew --version", "Checking Homebrew"):
            print("Please install Homebrew first: https://brew.sh/")
            return False
        
        if not run_command("brew install tesseract", "Installing Tesseract"):
            return False
    
    elif system == "windows":
        print("Windows detected. Please install Tesseract manually:")
        print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install and add to PATH")
        print("3. Update TESSERACT_PATH in .env if needed")
        
        # Check if tesseract is available
        if run_command("tesseract --version", "Checking Tesseract"):
            print("✓ Tesseract is already installed")
        else:
            print("⚠ Please install Tesseract and rerun this script")
            return False
    
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    print_header("Setting up Virtual Environment")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return True
    
    if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        return False
    
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print_header("Installing Python Dependencies")
    
    # Determine pip path based on OS
    system = platform.system().lower()
    if system == "windows":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"
    
    commands = [
        f"{pip_path} install --upgrade pip",
        f"{pip_path} install -r requirements.txt"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Running: {cmd}"):
            return False
    
    return True

def setup_environment_file():
    """Setup environment file"""
    print_header("Setting up Environment Configuration")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✓ Created .env file from .env.example")
        print("⚠ Please edit .env file and add your API keys")
    else:
        print("✗ .env.example not found")
        return False
    
    return True

def run_tests():
    """Run basic tests"""
    print_header("Running Basic Tests")
    
    system = platform.system().lower()
    if system == "windows":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    if not run_command(f"{python_path} -m pytest tests/ -v", "Running pytest"):
        print("⚠ Some tests failed, but this might be expected without API keys")
    
    return True

def display_next_steps():
    """Display next steps for the user"""
    print_header("Setup Complete! Next Steps")
    
    print("1. Edit the .env file and add your API keys:")
    print("   - GEMINI_API_KEY=your_gemini_key")
    print("   - OPENAI_API_KEY=your_openai_key")
    print("")
    print("2. Activate the virtual environment:")
    if platform.system().lower() == "windows":
        print("   .\\venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("")
    print("3. Start the API server:")
    print("   uvicorn app.main:app --reload")
    print("")
    print("4. Test the API:")
    print("   python test_api.py")
    print("")
    print("5. Access the API documentation:")
    print("   http://localhost:8000/docs")
    print("")
    print("6. For Docker deployment:")
    print("   docker-compose up --build")
    print("")

def main():
    """Main setup function"""
    print_header("GradeSense API Setup")
    
    steps = [
        ("Python Version Check", check_python_version),
        ("System Dependencies", install_system_dependencies),
        ("Virtual Environment", create_virtual_environment),
        ("Python Dependencies", install_python_dependencies),
        ("Environment Configuration", setup_environment_file),
        ("Basic Tests", run_tests)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"✗ {step_name} failed with exception: {e}")
            failed_steps.append(step_name)
    
    if failed_steps:
        print_header("Setup Completed with Warnings")
        print("The following steps had issues:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\nPlease resolve these issues before proceeding.")
    else:
        print_header("Setup Completed Successfully!")
    
    display_next_steps()

if __name__ == "__main__":
    main()
