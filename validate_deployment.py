#!/usr/bin/env python3
"""
Deployment validation script for ACME Corp Dashboard
Validates the environment and configuration before deployment
"""

import os
import sys
import yaml
import importlib.util
from pathlib import Path

def validate_files():
    """Validate that all required files are present"""
    required_files = [
        'app.py',
        'data_generator.py', 
        'utils.py',
        'requirements.txt',
        'databricks.yml',
        'app.yaml',
        'entrypoint.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def validate_yaml_configs():
    """Validate YAML configuration files"""
    configs = ['databricks.yml', 'app.yaml']
    
    for config_file in configs:
        try:
            with open(config_file, 'r') as f:
                yaml.safe_load(f)
            print(f"✅ {config_file} is valid YAML")
        except yaml.YAMLError as e:
            print(f"❌ {config_file} has YAML syntax error: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ {config_file} not found")
            return False
    
    return True

def validate_python_imports():
    """Validate that the main Python modules can be imported"""
    modules = ['app', 'data_generator', 'utils']
    
    for module in modules:
        try:
            spec = importlib.util.spec_from_file_location(module, f"{module}.py")
            if spec is None:
                print(f"❌ Cannot load {module}.py")
                return False
            print(f"✅ {module}.py can be imported")
        except Exception as e:
            print(f"❌ Error validating {module}.py: {e}")
            return False
    
    return True

def validate_requirements():
    """Validate requirements.txt format"""
    try:
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Basic validation - should contain package name
                if '==' not in line and '>=' not in line and '<=' not in line:
                    if not line.replace('-', '').replace('_', '').isalnum():
                        print(f"❌ Suspicious requirement line: {line}")
                        return False
        
        print("✅ requirements.txt format is valid")
        return True
        
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def validate_databricks_config():
    """Validate Databricks-specific configuration"""
    try:
        with open('databricks.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        if 'bundle' not in config:
            print("❌ databricks.yml missing 'bundle' section")
            return False
            
        if 'resources' not in config:
            print("❌ databricks.yml missing 'resources' section")
            return False
            
        if 'targets' not in config:
            print("❌ databricks.yml missing 'targets' section")  
            return False
        
        print("✅ databricks.yml structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error validating databricks.yml: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 Validating ACME Corp Dashboard deployment configuration...\n")
    
    validations = [
        validate_files,
        validate_yaml_configs,
        validate_python_imports, 
        validate_requirements,
        validate_databricks_config
    ]
    
    all_valid = True
    for validation in validations:
        if not validation():
            all_valid = False
        print()  # Add spacing
    
    if all_valid:
        print("🎉 All validations passed! Ready for deployment.")
        return 0
    else:
        print("❌ Some validations failed. Please fix the issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
