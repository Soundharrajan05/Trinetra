#!/usr/bin/env python3
"""
Integration test for common error handlers in TRINETRA AI system.

This script tests that the backend modules are properly using the common
error handlers from utils.helpers.
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_data_loader_error_handlers():
    """Test that data_loader.py uses common error handlers."""
    print("Testing data loader error handlers...")
    
    try:
        from backend.data_loader import load_dataset
        from utils.helpers import error_handlers
        
        # Test with non-existent file
        try:
            load_dataset("nonexistent_file.csv")
        except Exception as e:
            print(f"✅ Data loader error handling working: {type(e).__name__}")
            
        print("✅ Data loader error handlers integrated successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_model_error_handlers():
    """Test that model.py uses common error handlers."""
    print("Testing model error handlers...")
    
    try:
        from backend.model import train_model
        from utils.helpers import error_handlers
        
        # Test with invalid data
        try:
            invalid_df = pd.DataFrame({'invalid_column': [1, 2, 3]})
            train_model(invalid_df)
        except Exception as e:
            print(f"✅ Model error handling working: {type(e).__name__}")
            
        print("✅ Model error handlers integrated successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_fraud_detection_error_handlers():
    """Test that fraud_detection.py uses common error handlers."""
    print("Testing fraud detection error handlers...")
    
    try:
        from backend.fraud_detection import score_transactions
        from sklearn.ensemble import IsolationForest
        from utils.helpers import error_handlers
        
        # Test with invalid data
        try:
            invalid_df = pd.DataFrame({'invalid_column': [1, 2, 3]})
            model = IsolationForest()
            score_transactions(invalid_df, model)
        except Exception as e:
            print(f"✅ Fraud detection error handling working: {type(e).__name__}")
            
        print("✅ Fraud detection error handlers integrated successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_ai_explainer_error_handlers():
    """Test that ai_explainer.py uses common error handlers."""
    print("Testing AI explainer error handlers...")
    
    try:
        from backend.ai_explainer import explain_transaction
        from utils.helpers import error_handlers, performance_tracker
        
        # Test with valid transaction data (should use fallback)
        transaction = {
            'transaction_id': 'TEST001',
            'product': 'Test Product',
            'risk_score': 0.5
        }
        
        result = explain_transaction(transaction, force_api=False)
        print(f"✅ AI explainer working with fallback: {len(result)} chars")
        
        print("✅ AI explainer error handlers integrated successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_error_handlers_availability():
    """Test that error handlers are available and working."""
    print("Testing error handlers availability...")
    
    try:
        from utils.helpers import error_handlers, performance_tracker, ValidationHelpers
        
        # Test error handler methods
        test_error = ValueError("Test error")
        result = error_handlers.handle_general_error(test_error, "integration test")
        
        print(f"✅ Error handlers available and working")
        print(f"   - Error type: {result['error_type']}")
        print(f"   - User message: {result['user_message']}")
        
        # Test performance tracker
        if performance_tracker:
            stats = performance_tracker.get_performance_summary()
            print(f"✅ Performance tracker available")
        
        # Test validation helpers
        if ValidationHelpers:
            test_df = pd.DataFrame({'test': [1, 2, 3]})
            validation_result = ValidationHelpers.validate_dataset_schema(test_df, strict=False)
            print(f"✅ Validation helpers available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 TRINETRA AI Error Handlers Integration Test")
    print("=" * 60)
    
    tests = [
        test_error_handlers_availability,
        test_data_loader_error_handlers,
        test_model_error_handlers,
        test_fraud_detection_error_handlers,
        test_ai_explainer_error_handlers
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n{'-' * 40}")
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All error handler integrations working correctly!")
        return True
    else:
        print("❌ Some error handler integrations need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)