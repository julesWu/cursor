#!/usr/bin/env python3
"""
Entrypoint script for ACME Corp Dashboard in Databricks
This script handles the initialization and launch of the Streamlit app
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the environment for Databricks deployment"""
    
    # Set Streamlit configuration
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_SERVER_PORT"] = "8501"  
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
    os.environ["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
    
    # Databricks-specific configurations
    if "DATABRICKS_RUNTIME_VERSION" in os.environ:
        logger.info(f"Running on Databricks Runtime: {os.environ['DATABRICKS_RUNTIME_VERSION']}")
        os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    
    logger.info("Environment setup complete")

def install_requirements():
    """Install required packages if not already installed"""
    try:
        import streamlit
        import pandas 
        import plotly
        import faker
        logger.info("All required packages already installed")
    except ImportError as e:
        logger.info(f"Installing missing package: {e}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "streamlit==1.28.1", "pandas==2.1.2", "plotly==5.17.0", 
            "faker==19.13.0", "numpy==1.24.3"
        ])

def main():
    """Main entrypoint function"""
    logger.info("Starting ACME Corp Campaign Performance Dashboard")
    
    # Setup environment
    setup_environment()
    
    # Install requirements if needed
    install_requirements()
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")
    
    if not os.path.exists(app_path):
        logger.error(f"app.py not found at {app_path}")
        sys.exit(1)
    
    # Launch Streamlit app
    logger.info(f"Launching Streamlit app from {app_path}")
    
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.headless", "true",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ]
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Streamlit app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Streamlit app stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
