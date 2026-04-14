import os
import subprocess
import sys

def check_dependencies():
    """Ensure all dependencies are installed."""
    try:
        import streamlit
        import pandas
        import numpy
    except ImportError:
        print("Missing dependencies. Installing from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    print("Starting Seattle Polymarket Dashboard...")
    check_dependencies()
    
    # Initialize DB or run training pipeline if needed
    # You can add argument parsing here if you want to run specific parts
    
    # Run streamlit app
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    subprocess.run(["streamlit", "run", app_path])

if __name__ == "__main__":
    main()
