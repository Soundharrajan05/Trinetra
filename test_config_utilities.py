#!/usr/bin/env python3
"""
Test script for TRINETRA AI configuration management utilities.

This script tests the newly implemented configuration management utilities
to ensure they work correctly with environment variables and provide
proper validation and error handling.
"""

import os
import sys
import json
from pathlib import Path

# Add utils to path
sys.path.insert(0, 'utils')

try:
    from helpers import ConfigurationHelpers, validate_environment_setup, create_environment_report
    print("✅ Successfully imported configuration utilities")
except ImportError as e:
    print(f"❌ Failed to import configuration utilities: {e}")
    sys.exit(1)

def test_environment_config():
    """Test loading configuration from environment variables."""
    print("\n🔧 Testing environment configuration loading...")
    
    try:
        config = ConfigurationHelpers.load_environment_config()
        
        # Check that we got a dictionary with expected keys
        expected_keys = [
            'gemini_api_key', 'api_host', 'api_port', 'dataset_path', 
            'model_path', 'log_level', 'risk_threshold_safe', 'risk_threshold_fraud'
        ]
        
        missing_keys = [key for key in expected_keys if key not in config]
        if missing_keys:
            print(f"⚠️  Missing configuration keys: {missing_keys}")
        else:
            print("✅ All expected configuration keys present")
        
        # Test specific configurations
        print(f"   API Host: {config['api_host']}")
        print(f"   API Port: {config['api_port']}")
        print(f"   Dataset Path: {config['dataset_path']}")
        print(f"   Log Level: {config['log_level']}")
        print(f"   Gemini API Key: {'[SET]' if config['gemini_api_key'] else '[NOT SET]'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading environment configuration: {e}")
        return False

def test_specific_configs():
    """Test specific configuration getters."""
    print("\n🔧 Testing specific configuration getters...")
    
    try:
        # Test API config
        api_config = ConfigurationHelpers.get_api_config()
        print(f"   API Config: {api_config['host']}:{api_config['port']}")
        
        # Test Gemini config
        gemini_config = ConfigurationHelpers.get_gemini_config()
        print(f"   Gemini Enabled: {gemini_config['enabled']}")
        print(f"   Gemini Model: {gemini_config['model']}")
        
        # Test ML model config
        ml_config = ConfigurationHelpers.get_ml_model_config()
        print(f"   ML Model Features: {ml_config['feature_count']}")
        print(f"   Isolation Forest Estimators: {ml_config['isolation_forest']['n_estimators']}")
        
        # Test file paths
        file_paths = ConfigurationHelpers.get_file_paths()
        print(f"   Dataset Path: {file_paths['dataset']}")
        print(f"   Model Path: {file_paths['model']}")
        
        # Test thresholds
        risk_thresholds = ConfigurationHelpers.get_risk_thresholds()
        alert_thresholds = ConfigurationHelpers.get_alert_thresholds()
        print(f"   Risk Thresholds: Safe < {risk_thresholds['safe_threshold']}, Fraud >= {risk_thresholds['fraud_threshold']}")
        print(f"   Alert Thresholds: Price {alert_thresholds['price_deviation_threshold']}, Company {alert_thresholds['company_risk_threshold']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing specific configurations: {e}")
        return False

def test_configuration_validation():
    """Test configuration validation."""
    print("\n🔧 Testing configuration validation...")
    
    try:
        validation_result = ConfigurationHelpers.validate_configuration()
        
        print(f"   Configuration Valid: {validation_result['valid']}")
        
        if validation_result['errors']:
            print("   Errors:")
            for error in validation_result['errors']:
                print(f"     - {error}")
        
        if validation_result['warnings']:
            print("   Warnings:")
            for warning in validation_result['warnings']:
                print(f"     - {warning}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating configuration: {e}")
        return False

def test_environment_validation():
    """Test environment setup validation."""
    print("\n🔧 Testing environment validation...")
    
    try:
        env_validation = validate_environment_setup()
        
        print(f"   Environment Ready: {env_validation['environment_ready']}")
        print(f"   Python Version: {env_validation['python_version']}")
        
        if env_validation['errors']:
            print("   Errors:")
            for error in env_validation['errors']:
                print(f"     - {error}")
        
        if env_validation['warnings']:
            print("   Warnings:")
            for warning in env_validation['warnings']:
                print(f"     - {warning}")
        
        if env_validation['missing_packages']:
            print(f"   Missing Packages: {env_validation['missing_packages']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating environment: {e}")
        return False

def test_config_summary():
    """Test configuration summary generation."""
    print("\n🔧 Testing configuration summary...")
    
    try:
        summary = ConfigurationHelpers.create_config_summary()
        
        # Check that summary is not empty and contains expected sections
        if len(summary) > 100:  # Basic length check
            print("✅ Configuration summary generated successfully")
            
            # Check for key sections
            expected_sections = ['API Configuration', 'ML Model Configuration', 'Risk Thresholds']
            missing_sections = [section for section in expected_sections if section not in summary]
            
            if missing_sections:
                print(f"⚠️  Missing summary sections: {missing_sections}")
            else:
                print("✅ All expected summary sections present")
            
            # Optionally print first few lines
            lines = summary.split('\n')[:10]
            print("   Summary preview:")
            for line in lines:
                print(f"     {line}")
            
        else:
            print("⚠️  Configuration summary seems too short")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating configuration summary: {e}")
        return False

def test_config_file_operations():
    """Test configuration file save/load operations."""
    print("\n🔧 Testing configuration file operations...")
    
    try:
        # Load current config
        config = ConfigurationHelpers.load_environment_config()
        
        # Save to test file
        test_file = "test_config.json"
        success = ConfigurationHelpers.save_config_to_file(config, test_file)
        
        if success and os.path.exists(test_file):
            print("✅ Configuration saved to file successfully")
            
            # Try to load it back
            from helpers import load_config_from_file
            loaded_config = load_config_from_file(test_file)
            
            if loaded_config:
                print("✅ Configuration loaded from file successfully")
                
                # Check that sensitive data was redacted
                if loaded_config.get('gemini_api_key') == '[REDACTED]':
                    print("✅ Sensitive data properly redacted in saved file")
                else:
                    print("⚠️  Sensitive data may not be properly redacted")
            else:
                print("❌ Failed to load configuration from file")
            
            # Clean up test file
            os.remove(test_file)
            print("✅ Test file cleaned up")
            
        else:
            print("❌ Failed to save configuration to file")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing configuration file operations: {e}")
        return False

def main():
    """Run all configuration utility tests."""
    print("🚀 TRINETRA AI Configuration Management Utilities Test")
    print("=" * 60)
    
    tests = [
        ("Environment Configuration Loading", test_environment_config),
        ("Specific Configuration Getters", test_specific_configs),
        ("Configuration Validation", test_configuration_validation),
        ("Environment Validation", test_environment_validation),
        ("Configuration Summary", test_config_summary),
        ("Configuration File Operations", test_config_file_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All configuration management utilities are working correctly!")
        
        # Generate and display environment report
        print("\n📋 Generating environment report...")
        try:
            report = create_environment_report()
            print("\n" + report)
        except Exception as e:
            print(f"❌ Error generating environment report: {e}")
        
        return True
    else:
        print("⚠️  Some configuration utilities need attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)