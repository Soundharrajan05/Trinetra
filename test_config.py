#!/usr/bin/env python3
"""
Test script for TRINETRA AI configuration management utilities.
"""

import sys
import os
sys.path.append('.')

from utils.helpers import (
    ConfigurationHelpers, 
    get_system_config, 
    initialize_system_configuration, 
    get_configuration_health_check
)

def test_configuration_utilities():
    """Test all configuration management utilities."""
    print("Testing TRINETRA AI Configuration Management Utilities")
    print("=" * 60)
    
    # Test 1: Load environment config
    print("\n1. Testing environment configuration loading...")
    try:
        env_config = ConfigurationHelpers.load_environment_config()
        print(f"✓ Environment config loaded: {len(env_config)} settings")
        
        # Show some key settings (without sensitive data)
        key_settings = ['api_host', 'api_port', 'dashboard_host', 'dashboard_port', 'environment']
        for key in key_settings:
            if key in env_config:
                print(f"  {key}: {env_config[key]}")
                
    except Exception as e:
        print(f"✗ Environment config failed: {e}")
    
    # Test 2: Get system config
    print("\n2. Testing system configuration...")
    try:
        system_config = get_system_config()
        print(f"✓ System config loaded: {len(system_config)} sections")
        print(f"  Sections: {list(system_config.keys())}")
    except Exception as e:
        print(f"✗ System config failed: {e}")
    
    # Test 3: Configuration validation
    print("\n3. Testing configuration validation...")
    try:
        validation = ConfigurationHelpers.validate_configuration()
        status = "VALID" if validation['valid'] else "INVALID"
        print(f"✓ Configuration validation: {status}")
        
        if validation.get('errors'):
            print(f"  Errors: {len(validation['errors'])}")
            for error in validation['errors'][:3]:  # Show first 3 errors
                print(f"    - {error}")
                
        if validation.get('warnings'):
            print(f"  Warnings: {len(validation['warnings'])}")
            for warning in validation['warnings'][:3]:  # Show first 3 warnings
                print(f"    - {warning}")
                
    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
    
    # Test 4: Health check
    print("\n4. Testing configuration health check...")
    try:
        health = get_configuration_health_check()
        print(f"✓ Health check completed: {health['overall_status']} (Score: {health['health_score']}%)")
        
        if health.get('checks'):
            print("  Check results:")
            for check_name, check_result in health['checks'].items():
                print(f"    {check_name}: {check_result['status']}")
                
    except Exception as e:
        print(f"✗ Health check failed: {e}")
    
    # Test 5: Specific configuration getters
    print("\n5. Testing specific configuration getters...")
    
    config_getters = [
        ('API Config', ConfigurationHelpers.get_api_config),
        ('Gemini Config', ConfigurationHelpers.get_gemini_config),
        ('ML Model Config', ConfigurationHelpers.get_ml_model_config),
        ('File Paths', ConfigurationHelpers.get_file_paths),
        ('Risk Thresholds', ConfigurationHelpers.get_risk_thresholds),
        ('Alert Thresholds', ConfigurationHelpers.get_alert_thresholds)
    ]
    
    for name, getter_func in config_getters:
        try:
            config = getter_func()
            print(f"✓ {name}: {len(config)} settings")
        except Exception as e:
            print(f"✗ {name} failed: {e}")
    
    print("\n" + "=" * 60)
    print("Configuration management utilities test completed!")

if __name__ == "__main__":
    test_configuration_utilities()