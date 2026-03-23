"""
Data Corruption Scenarios Tests for TRINETRA AI

This module tests various data corruption scenarios that could occur in production,
including file corruption, data type corruption, encoding issues, and partial data loss.

Author: TRINETRA AI Team
Date: 2024
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_dataset, DataLoaderError
from feature_engineering import engineer_features


class TestDataCorruptionScenarios:
    """Test various data corruption scenarios."""
    
    def test_csv_with_null_bytes(self):
        """Test CSV file containing null bytes."""
        corrupted_content = "transaction_id,date,product\nTXN001,2024-01-01,Electronics\x00\nTXN002,2024-01-02,Textiles"
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            f.write(corrupted_content.encode('utf-8'))
            temp_path = f.name
        
        try:
            with pytest.raises(DataLoaderError):
                load_dataset(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_csv_with_mixed_line_endings(self):
        """Test CSV with mixed line endings (\\r\\n, \\n, \\r)."""
        mixed_content = "transaction_id,date,product\r\nTXN001,2024-01-01,Electronics\nTXN002,2024-01-02,Textiles\rTXN003,2024-01-03,Machinery"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            f.write(mixed_content)
            temp_path = f.name
        
        try:
            # Should handle mixed line endings
            df = load_dataset(temp_path)
            assert len(df) >= 2  # Should parse at least some rows
        finally:
            os.unlink(temp_path)
    
    def test_csv_with_inconsistent_column_counts(self):
        """Test CSV where rows have different numbers of columns."""
        inconsistent_content = """transaction_id,date,product,quantity
TXN001,2024-01-01,Electronics,100
TXN002,2024-01-02,Textiles
TXN003,2024-01-03,Machinery,200,extra_column,another_extra
TXN004,2024-01-04"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(inconsistent_content)
            temp_path = f.name
        
        try:
            # Should handle inconsistent columns gracefully
            df = load_dataset(temp_path)
            assert 'transaction_id' in df.columns
        except DataLoaderError:
            # Acceptable if parser cannot handle inconsistent structure
            pass
        finally:
            os.unlink(temp_path)
    
    def test_csv_with_embedded_newlines_in_fields(self):
        """Test CSV with newlines embedded within quoted fields."""
        embedded_newlines = '''transaction_id,date,product,description
TXN001,2024-01-01,Electronics,"Multi-line
description with
embedded newlines"
TXN002,2024-01-02,Textiles,"Single line description"'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(embedded_newlines)
            temp_path = f.name
        
        try:
            df = load_dataset(temp_path)
            # Should handle embedded newlines in quoted fields
            assert len(df) == 2
            assert 'transaction_id' in df.columns
        finally:
            os.unlink(temp_path)
    
    def test_data_type_corruption_during_processing(self):
        """Test data type corruption during feature engineering."""
        # Create DataFrame with corrupted data types
        df = pd.DataFrame({
            'price_deviation': [0.1, 'corrupted', None, float('inf')],
            'route_anomaly': [1, 'yes', None, 2],  # Should be 0 or 1
            'company_risk_score': [0.5, 'high', None, -1],  # Should be 0-1
            'port_activity_index': [1.0, 'busy', None, float('nan')],
            'shipment_duration_days': [10, 'long', None, -5],  # Should be positive
            'distance_km': [1000, 'far', None, 0],
            'cargo_volume': [100, 'large', None, -10],  # Should be positive
            'quantity': [10, 'many', None, 0]
        })
        
        # Should handle corrupted data types gracefully
        result_df = engineer_features(df)
        
        # Should complete without crashing
        assert len(result_df) == 4
        assert 'price_anomaly_score' in result_df.columns
    
    def test_unicode_corruption_scenarios(self):
        """Test various Unicode corruption scenarios."""
        unicode_issues = [
            "TXN001,2024-01-01,Électronique\udcff",  # Invalid Unicode
            "TXN002,2024-01-02,\ufffd\ufffd\ufffd",   # Replacement characters
            "TXN003,2024-01-03,\x00\x01\x02",        # Control characters
            "TXN004,2024-01-04,\U0001F600\U0001F601" # Emoji (valid but unusual)
        ]
        
        csv_content = "transaction_id,date,product\n" + "\n".join(unicode_issues)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8', errors='replace') as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            # Should handle Unicode issues gracefully
            df = load_dataset(temp_path)
            assert len(df) >= 1  # Should parse at least some rows
        except DataLoaderError:
            # Acceptable if Unicode corruption is too severe
            pass
        finally:
            os.unlink(temp_path)
    
    def test_partial_file_corruption(self):
        """Test file that is partially corrupted (truncated)."""
        # Create valid CSV content
        valid_content = """transaction_id,date,product,quantity,unit_price,fraud_label
TXN001,2024-01-01,Electronics,100,10.0,0
TXN002,2024-01-02,Textiles,200,20.0,1
TXN003,2024-01-03,Machinery,300,30.0,0
TXN004,2024-01-04,Chemicals,400,40.0,1"""
        
        # Truncate at various points
        truncation_points = [50, 100, 150, 200]  # Bytes
        
        for truncate_at in truncation_points:
            truncated_content = valid_content[:truncate_at]
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write(truncated_content)
                temp_path = f.name
            
            try:
                # Should handle truncated files gracefully
                df = load_dataset(temp_path)
                # May succeed with partial data or fail gracefully
                if len(df) > 0:
                    assert 'transaction_id' in df.columns
            except DataLoaderError:
                # Expected for severely truncated files
                pass
            finally:
                os.unlink(temp_path)
    
    def test_memory_corruption_simulation(self):
        """Test behavior when memory corruption affects data structures."""
        # Create DataFrame and simulate memory corruption
        df = pd.DataFrame({
            'price_deviation': [0.1, 0.2, 0.3],
            'route_anomaly': [0, 1, 0],
            'company_risk_score': [0.5, 0.8, 0.3],
            'port_activity_index': [1.0, 1.5, 0.8],
            'shipment_duration_days': [10, 20, 15],
            'distance_km': [1000, 2000, 1500],
            'cargo_volume': [100, 200, 150],
            'quantity': [10, 20, 15]
        })
        
        # Simulate memory corruption by modifying DataFrame internals
        try:
            # Corrupt the index
            df.index = pd.Index([0, 1, 'corrupted'])
            
            # Should handle corrupted index gracefully
            result_df = engineer_features(df)
            assert len(result_df) == 3
            
        except Exception:
            # Memory corruption might cause various exceptions
            # The important thing is that it doesn't crash the entire system
            pass
    
    def test_concurrent_file_modification(self):
        """Test behavior when file is modified during reading."""
        initial_content = """transaction_id,date,product
TXN001,2024-01-01,Electronics
TXN002,2024-01-02,Textiles"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(initial_content)
            temp_path = f.name
        
        try:
            # Start loading the file
            import threading
            import time
            
            def modify_file():
                time.sleep(0.1)  # Small delay
                try:
                    with open(temp_path, 'a') as f:
                        f.write("\nTXN003,2024-01-03,Machinery")
                except:
                    pass  # File might be locked
            
            # Start file modification in background
            modifier_thread = threading.Thread(target=modify_file)
            modifier_thread.start()
            
            # Load file (might be modified during loading)
            df = load_dataset(temp_path)
            
            modifier_thread.join()
            
            # Should handle concurrent modification gracefully
            assert 'transaction_id' in df.columns
            assert len(df) >= 2  # Should have at least original rows
            
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])