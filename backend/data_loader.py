"""
Data Loader Module for TRINETRA AI Trade Fraud Detection System

This module handles loading and validation of trade transaction data from CSV files.
It includes date parsing, missing value handling, and schema validation with comprehensive
error handling and logging for production-ready operation.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
import os
import sys
from pathlib import Path

# Import common error handlers
try:
    from utils.helpers import error_handlers, ValidationHelpers, performance_tracker
except ImportError:
    # Fallback if utils.helpers is not available
    error_handlers = None
    ValidationHelpers = None
    performance_tracker = None

# Configure comprehensive logging
def setup_logging():
    """Set up comprehensive logging configuration for the data loader."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging with both file and console handlers
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'trinetra_data_loader.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Required columns for schema validation
REQUIRED_COLUMNS = [
    'transaction_id', 'date', 'product', 'commodity_category', 'quantity',
    'unit_price', 'trade_value', 'market_price', 'price_deviation',
    'exporter_company', 'exporter_country', 'importer_company', 'importer_country',
    'shipping_route', 'distance_km', 'company_risk_score', 'route_anomaly', 'fraud_label'
]

# Data quality thresholds
DATA_QUALITY_THRESHOLDS = {
    'max_missing_percentage': 0.1,  # 10% max missing values per column
    'min_rows': 100,  # Minimum number of rows required
    'max_duplicate_percentage': 0.05,  # 5% max duplicate transactions
}

class DataLoaderError(Exception):
    """Custom exception for data loader errors."""
    pass

class SchemaValidationError(DataLoaderError):
    """Exception raised when schema validation fails."""
    pass

class DataQualityError(DataLoaderError):
    """Exception raised when data quality checks fail."""
    pass

def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load CSV dataset with comprehensive error handling, validation, and logging.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Clean DataFrame ready for feature engineering
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        SchemaValidationError: If schema validation fails
        DataQualityError: If data quality checks fail
        DataLoaderError: For other data loading issues
    """
    logger.info(f"Starting dataset load operation from: {file_path}")
    
    try:
        # Validate file path and existence
        _validate_file_path(file_path)
        
        # Load the CSV file with comprehensive error handling
        df = _load_csv_file(file_path)
        
        # Validate schema using common validation helpers
        if ValidationHelpers:
            validation_result = ValidationHelpers.validate_dataset_schema(df, strict=False)
            if not validation_result['valid']:
                if error_handlers:
                    error_info = error_handlers.handle_schema_validation_error(
                        validation_result, "dataset loading"
                    )
                    if not error_info['can_continue']:
                        raise SchemaValidationError(error_info['user_message'])
                    else:
                        logger.warning(f"Schema validation warnings: {error_info['user_message']}")
                else:
                    # Fallback to original validation
                    _validate_dataset_schema(df)
        else:
            # Fallback to original validation
            _validate_dataset_schema(df)
        
        # Perform data quality checks
        _perform_data_quality_checks(df)
        
        # Handle missing values
        df = handle_missing_values(df)
        
        # Normalize fraud labels: 0 -> SAFE, 2 -> FRAUD
        if 'fraud_label' in df.columns:
            logger.info("Normalizing fraud labels (0 -> SAFE, 2 -> FRAUD)")
            df["fraud_label_normalized"] = df["fraud_label"].map({0: "SAFE", 2: "FRAUD"})
            # Fill any unmapped values with original label as string
            df["fraud_label_normalized"] = df["fraud_label_normalized"].fillna(df["fraud_label"].astype(str))
            logger.info(f"Fraud label normalization complete. Distribution: {df['fraud_label_normalized'].value_counts().to_dict()}")
        
        # Final validation after processing
        _validate_processed_data(df)
        
        # Log successful completion with performance tracking
        if performance_tracker:
            performance_tracker.log_dataset_load(0.0, len(df), file_path)  # Time will be tracked elsewhere
        
        stats = get_dataset_stats(df)
        logger.info(f"Dataset loaded successfully. Final statistics: {stats}")
        logger.info(f"Dataset load operation completed successfully for {file_path}")
        
        return df
        
    except (FileNotFoundError, SchemaValidationError, DataQualityError) as e:
        logger.error(f"Dataset load failed: {e}")
        raise
    except pd.errors.EmptyDataError as e:
        if error_handlers:
            error_info = error_handlers.handle_csv_loading_error(e, file_path)
            raise DataLoaderError(error_info['user_message']) from e
        else:
            error_msg = f"CSV file is empty: {file_path}"
            logger.error(error_msg)
            raise DataLoaderError(error_msg) from e
    except pd.errors.ParserError as e:
        if error_handlers:
            error_info = error_handlers.handle_csv_loading_error(e, file_path)
            raise DataLoaderError(error_info['user_message']) from e
        else:
            error_msg = f"CSV parsing error: {e}"
            logger.error(error_msg)
            raise DataLoaderError(error_msg) from e
    except MemoryError as e:
        if error_handlers:
            error_info = error_handlers.handle_general_error(e, "dataset loading")
            raise DataLoaderError(error_info['user_message']) from e
        else:
            error_msg = f"Insufficient memory to load dataset: {file_path}"
            logger.error(error_msg)
            raise DataLoaderError(error_msg) from e
    except Exception as e:
        if error_handlers:
            error_info = error_handlers.handle_general_error(e, "dataset loading")
            raise DataLoaderError(error_info['user_message']) from e
        else:
            error_msg = f"Unexpected error loading dataset from {file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise DataLoaderError(error_msg) from e

def _validate_file_path(file_path: str) -> None:
    """
    Validate file path and existence with detailed logging.
    
    Args:
        file_path (str): Path to validate
        
    Raises:
        FileNotFoundError: If file doesn't exist or path is invalid
    """
    logger.debug(f"Validating file path: {file_path}")
    
    if not file_path:
        raise FileNotFoundError("File path cannot be empty")
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        # Log current working directory for debugging
        logger.debug(f"Current working directory: {os.getcwd()}")
        # Log directory contents if parent directory exists
        parent_dir = os.path.dirname(file_path)
        if os.path.exists(parent_dir):
            try:
                files = os.listdir(parent_dir)
                logger.debug(f"Files in {parent_dir}: {files}")
            except PermissionError:
                logger.debug(f"Permission denied accessing directory: {parent_dir}")
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Path exists but is not a file: {file_path}")
    
    # Check file permissions
    if not os.access(file_path, os.R_OK):
        raise FileNotFoundError(f"File exists but is not readable: {file_path}")
    
    # Check file size
    file_size = os.path.getsize(file_path)
    logger.info(f"File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    
    if file_size == 0:
        raise FileNotFoundError(f"File is empty: {file_path}")
    
    logger.debug(f"File path validation successful: {file_path}")

def _load_csv_file(file_path: str) -> pd.DataFrame:
    """
    Load CSV file with comprehensive error handling and logging.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Loaded DataFrame
        
    Raises:
        DataLoaderError: If CSV loading fails
    """
    logger.info(f"Loading CSV file: {file_path}")
    
    try:
        # First, try to read without date parsing to check if date column exists
        df_preview = pd.read_csv(file_path, nrows=0)  # Just read headers
        
        # Check if date column exists before parsing
        parse_dates = ['date'] if 'date' in df_preview.columns else None
        
        # Read CSV with conditional date parsing and error handling
        df = pd.read_csv(
            file_path,
            parse_dates=parse_dates,  # Only parse dates if date column exists
            low_memory=False,
            encoding='utf-8'  # Explicit encoding
        )
        
        logger.info(f"CSV loaded successfully. Shape: {df.shape}")
        logger.debug(f"Columns found: {list(df.columns)}")
        
        return df
        
    except UnicodeDecodeError as e:
        # Try alternative encodings
        logger.warning(f"UTF-8 encoding failed, trying alternative encodings: {e}")
        for encoding in ['latin-1', 'iso-8859-1', 'cp1252']:
            try:
                logger.info(f"Attempting to load with {encoding} encoding")
                
                # Check for date column with alternative encoding
                df_preview = pd.read_csv(file_path, nrows=0, encoding=encoding)
                parse_dates = ['date'] if 'date' in df_preview.columns else None
                
                df = pd.read_csv(
                    file_path,
                    parse_dates=parse_dates,
                    low_memory=False,
                    encoding=encoding
                )
                logger.info(f"Successfully loaded with {encoding} encoding")
                return df
            except UnicodeDecodeError:
                continue
        
        error_msg = f"Failed to decode CSV file with any supported encoding: {file_path}"
        logger.error(error_msg)
        raise DataLoaderError(error_msg) from e

def validate_schema(df: pd.DataFrame) -> bool:
    """
    Ensure required columns exist in the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        
    Returns:
        bool: True if schema is valid, False otherwise
    """
    logger.info("Starting schema validation")
    return _validate_dataset_schema(df, raise_on_error=False)

def _validate_dataset_schema(df: pd.DataFrame, raise_on_error: bool = True) -> bool:
    """
    Internal schema validation with comprehensive error handling.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        raise_on_error (bool): Whether to raise exceptions on validation failure
        
    Returns:
        bool: True if schema is valid
        
    Raises:
        SchemaValidationError: If schema validation fails and raise_on_error is True
    """
    logger.debug("Performing comprehensive schema validation")
    
    validation_errors = []
    
    # Check for required columns
    missing_columns = []
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            missing_columns.append(col)
    
    if missing_columns:
        error_msg = f"Missing required columns: {missing_columns}"
        validation_errors.append(error_msg)
        logger.error(error_msg)
    
    # Check for duplicate columns
    duplicate_columns = df.columns[df.columns.duplicated()].tolist()
    if duplicate_columns:
        error_msg = f"Duplicate columns found: {duplicate_columns}"
        validation_errors.append(error_msg)
        logger.error(error_msg)
    
    # Validate data types for critical columns
    try:
        # Check if date column exists and is parseable
        if 'date' in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df['date']):
                logger.warning("Date column is not in datetime format, attempting conversion")
                try:
                    df['date'] = pd.to_datetime(df['date'])
                    logger.info("Successfully converted date column to datetime")
                except Exception as e:
                    error_msg = f"Failed to convert date column to datetime: {e}"
                    validation_errors.append(error_msg)
                    logger.error(error_msg)
        
        # Check numeric columns
        numeric_columns = ['quantity', 'unit_price', 'trade_value', 'market_price', 
                          'price_deviation', 'distance_km', 'company_risk_score', 
                          'route_anomaly', 'fraud_label']
        
        for col in numeric_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    logger.warning(f"Column {col} is not numeric, attempting conversion")
                    try:
                        original_nulls = df[col].isnull().sum()
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        new_nulls = df[col].isnull().sum()
                        conversion_failures = new_nulls - original_nulls
                        
                        if conversion_failures > 0:
                            logger.warning(f"Failed to convert {conversion_failures} values in column {col} to numeric")
                        else:
                            logger.info(f"Successfully converted column {col} to numeric")
                    except Exception as e:
                        error_msg = f"Failed to convert column {col} to numeric: {e}"
                        validation_errors.append(error_msg)
                        logger.error(error_msg)
        
        # Validate transaction_id uniqueness
        if 'transaction_id' in df.columns:
            duplicate_ids = df['transaction_id'].duplicated().sum()
            if duplicate_ids > 0:
                logger.warning(f"Found {duplicate_ids} duplicate transaction IDs")
        
        # Validate fraud_label values
        if 'fraud_label' in df.columns:
            unique_labels = set(df['fraud_label'].dropna().unique())
            # Allow for different fraud labeling schemes (0/1, 0/2, etc.)
            if len(unique_labels) > 0:
                min_label = min(unique_labels)
                max_label = max(unique_labels)
                
                # Check if labels are reasonable (should be integers, not too many unique values)
                if len(unique_labels) > 5:
                    logger.warning(f"Fraud labels have many unique values ({len(unique_labels)}): {unique_labels}")
                elif not all(isinstance(x, (int, np.integer)) for x in unique_labels):
                    logger.warning(f"Fraud labels contain non-integer values: {unique_labels}")
                else:
                    logger.info(f"Fraud labels validation passed. Unique values: {sorted(unique_labels)}")
            else:
                logger.warning("No valid fraud_label values found")
        
    except Exception as e:
        error_msg = f"Unexpected error during data type validation: {e}"
        validation_errors.append(error_msg)
        logger.error(error_msg, exc_info=True)
    
    # Report validation results
    if validation_errors:
        error_summary = f"Schema validation failed with {len(validation_errors)} errors: {'; '.join(validation_errors)}"
        logger.error(error_summary)
        if raise_on_error:
            raise SchemaValidationError(error_summary)
        return False
    else:
        logger.info("Schema validation passed successfully")
        return True

def _perform_data_quality_checks(df: pd.DataFrame) -> None:
    """
    Perform comprehensive data quality checks with detailed logging.
    
    Args:
        df (pd.DataFrame): DataFrame to check
        
    Raises:
        DataQualityError: If data quality checks fail
    """
    logger.info("Performing data quality checks")
    
    quality_issues = []
    
    # Check minimum row count
    if len(df) < DATA_QUALITY_THRESHOLDS['min_rows']:
        error_msg = f"Dataset has only {len(df)} rows, minimum required: {DATA_QUALITY_THRESHOLDS['min_rows']}"
        quality_issues.append(error_msg)
        logger.error(error_msg)
    
    # Check for excessive missing values per column
    for column in df.columns:
        missing_count = df[column].isnull().sum()
        missing_percentage = missing_count / len(df)
        
        if missing_percentage > DATA_QUALITY_THRESHOLDS['max_missing_percentage']:
            error_msg = f"Column '{column}' has {missing_percentage:.1%} missing values (threshold: {DATA_QUALITY_THRESHOLDS['max_missing_percentage']:.1%})"
            quality_issues.append(error_msg)
            logger.warning(error_msg)
    
    # Check for excessive duplicate transactions
    if 'transaction_id' in df.columns:
        duplicate_count = df['transaction_id'].duplicated().sum()
        duplicate_percentage = duplicate_count / len(df)
        
        if duplicate_percentage > DATA_QUALITY_THRESHOLDS['max_duplicate_percentage']:
            error_msg = f"Dataset has {duplicate_percentage:.1%} duplicate transactions (threshold: {DATA_QUALITY_THRESHOLDS['max_duplicate_percentage']:.1%})"
            quality_issues.append(error_msg)
            logger.warning(error_msg)
    
    # Check for data consistency issues
    if 'trade_value' in df.columns and 'quantity' in df.columns and 'unit_price' in df.columns:
        try:
            # Check if trade_value approximately equals quantity * unit_price
            # First ensure columns are numeric
            quantity_numeric = pd.to_numeric(df['quantity'], errors='coerce')
            unit_price_numeric = pd.to_numeric(df['unit_price'], errors='coerce')
            trade_value_numeric = pd.to_numeric(df['trade_value'], errors='coerce')
            
            # Only check consistency for rows where all values are numeric
            valid_rows = quantity_numeric.notna() & unit_price_numeric.notna() & trade_value_numeric.notna()
            
            if valid_rows.sum() > 0:
                calculated_value = quantity_numeric[valid_rows] * unit_price_numeric[valid_rows]
                value_diff = abs(trade_value_numeric[valid_rows] - calculated_value)
                inconsistent_rows = (value_diff > 0.01).sum()  # Allow for small rounding differences
                
                if inconsistent_rows > 0:
                    inconsistent_percentage = inconsistent_rows / valid_rows.sum()
                    logger.warning(f"Found {inconsistent_rows} rows ({inconsistent_percentage:.1%}) with inconsistent trade_value calculations")
            else:
                logger.warning("Cannot perform trade value consistency check - numeric data not available")
        except Exception as e:
            logger.warning(f"Trade value consistency check failed: {e}")
    
    # Log data quality summary
    if quality_issues:
        logger.warning(f"Data quality check completed with {len(quality_issues)} issues identified")
        # For now, we'll log warnings but not fail the load - this can be adjusted based on requirements
        for issue in quality_issues:
            logger.warning(f"Data quality issue: {issue}")
    else:
        logger.info("Data quality checks passed successfully")

def _validate_processed_data(df: pd.DataFrame) -> None:
    """
    Validate data after processing to ensure it's ready for feature engineering.
    
    Args:
        df (pd.DataFrame): Processed DataFrame to validate
        
    Raises:
        DataQualityError: If processed data validation fails
    """
    logger.debug("Validating processed data")
    
    # Check that we still have data after processing
    if len(df) == 0:
        raise DataQualityError("No data remaining after processing")
    
    # Check that critical columns have no missing values after processing
    critical_columns = ['transaction_id', 'date', 'fraud_label']
    for col in critical_columns:
        if col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                raise DataQualityError(f"Critical column '{col}' still has {missing_count} missing values after processing")
    
    logger.debug("Processed data validation completed successfully")

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values using forward fill or mean imputation with comprehensive logging.
    
    Args:
        df (pd.DataFrame): DataFrame with potential missing values
        
    Returns:
        pd.DataFrame: DataFrame with missing values handled
        
    Raises:
        DataQualityError: If missing value handling fails critically
    """
    logger.info("Starting missing value handling process")
    
    try:
        # Create a copy to avoid modifying the original
        df_processed = df.copy()
        
        # Count missing values before processing
        missing_before = df_processed.isnull().sum().sum()
        if missing_before > 0:
            logger.warning(f"Found {missing_before} missing values across all columns")
            
            # Log missing values per column
            missing_per_column = df_processed.isnull().sum()
            for col, count in missing_per_column[missing_per_column > 0].items():
                percentage = (count / len(df_processed)) * 100
                logger.warning(f"Column '{col}': {count} missing values ({percentage:.1f}%)")
        else:
            logger.info("No missing values found in dataset")
            return df_processed
        
        # Handle missing values by column type and importance
        for column in df_processed.columns:
            missing_count = df_processed[column].isnull().sum()
            
            if missing_count > 0:
                logger.debug(f"Processing missing values in column '{column}'")
                
                try:
                    # Critical columns - more strict handling
                    if column in ['transaction_id', 'date']:
                        logger.error(f"Critical column '{column}' has missing values - this may indicate data corruption")
                        # For transaction_id, we could generate IDs, but this might indicate serious data issues
                        if column == 'transaction_id':
                            # Generate missing transaction IDs
                            mask = df_processed[column].isnull()
                            df_processed.loc[mask, column] = [f"GENERATED_TXN_{i}" for i in range(mask.sum())]
                            logger.warning(f"Generated {mask.sum()} missing transaction IDs")
                    
                    # Numeric columns - use statistical imputation
                    elif pd.api.types.is_numeric_dtype(df_processed[column]):
                        if column in ['fraud_label']:
                            # For fraud_label, use mode (most common value)
                            mode_value = df_processed[column].mode()
                            if len(mode_value) > 0:
                                fill_value = mode_value[0]
                                df_processed[column].fillna(fill_value, inplace=True)
                                logger.info(f"Filled {missing_count} missing values in '{column}' with mode: {fill_value}")
                            else:
                                # If no mode available, use 0 (assuming 0 = not fraud)
                                df_processed[column].fillna(0, inplace=True)
                                logger.warning(f"No mode available for '{column}', filled with 0")
                        else:
                            # For other numeric columns, use median (more robust than mean)
                            median_value = df_processed[column].median()
                            if pd.notna(median_value):
                                df_processed[column].fillna(median_value, inplace=True)
                                logger.info(f"Filled {missing_count} missing values in '{column}' with median: {median_value:.2f}")
                            else:
                                # If median is also NaN, use 0
                                df_processed[column].fillna(0, inplace=True)
                                logger.warning(f"Median not available for '{column}', filled with 0")
                    
                    # Categorical columns - use forward/backward fill then mode
                    else:
                        # Try forward fill first
                        df_processed[column] = df_processed[column].ffill()
                        
                        # Then backward fill
                        df_processed[column] = df_processed[column].bfill()
                        
                        # Check if there are still missing values
                        remaining_missing = df_processed[column].isnull().sum()
                        if remaining_missing > 0:
                            # Use mode if available
                            mode_value = df_processed[column].mode()
                            if len(mode_value) > 0:
                                df_processed[column].fillna(mode_value[0], inplace=True)
                                logger.info(f"Filled {remaining_missing} remaining missing values in '{column}' with mode: {mode_value[0]}")
                            else:
                                # Last resort: fill with 'Unknown'
                                df_processed[column].fillna('Unknown', inplace=True)
                                logger.warning(f"Filled {remaining_missing} remaining missing values in '{column}' with 'Unknown'")
                        else:
                            logger.info(f"Successfully filled missing values in '{column}' using forward/backward fill")
                
                except Exception as e:
                    logger.error(f"Error handling missing values in column '{column}': {e}")
                    # Continue with other columns rather than failing completely
                    continue
        
        # Count missing values after processing
        missing_after = df_processed.isnull().sum().sum()
        
        # Log summary
        logger.info(f"Missing value handling completed. Before: {missing_before}, After: {missing_after}")
        
        if missing_after > 0:
            logger.warning(f"Still have {missing_after} missing values after processing")
            # Log which columns still have missing values
            remaining_missing = df_processed.isnull().sum()
            for col, count in remaining_missing[remaining_missing > 0].items():
                logger.warning(f"Column '{col}' still has {count} missing values")
        
        # Validate that critical columns have no missing values
        critical_columns = ['transaction_id', 'date']
        for col in critical_columns:
            if col in df_processed.columns:
                missing_critical = df_processed[col].isnull().sum()
                if missing_critical > 0:
                    raise DataQualityError(f"Critical column '{col}' still has {missing_critical} missing values after processing")
        
        return df_processed
        
    except Exception as e:
        error_msg = f"Failed to handle missing values: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise DataQualityError(error_msg) from e

def get_dataset_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Return comprehensive statistics about the dataset with error handling.
    
    Args:
        df (pd.DataFrame): DataFrame to analyze
        
    Returns:
        dict: Dictionary containing detailed dataset statistics
    """
    logger.debug("Calculating dataset statistics")
    
    try:
        stats = {
            'basic_info': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            },
            'data_quality': {
                'missing_values': df.isnull().sum().sum(),
                'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                'duplicate_rows': df.duplicated().sum(),
            }
        }
        
        # Date range information
        if 'date' in df.columns:
            try:
                date_min = df['date'].min()
                date_max = df['date'].max()
                stats['date_range'] = {
                    'start': date_min.strftime('%Y-%m-%d') if pd.notna(date_min) else None,
                    'end': date_max.strftime('%Y-%m-%d') if pd.notna(date_max) else None,
                    'span_days': (date_max - date_min).days if pd.notna(date_min) and pd.notna(date_max) else None
                }
            except Exception as e:
                logger.warning(f"Error calculating date range: {e}")
                stats['date_range'] = {'error': str(e)}
        
        # Fraud distribution
        if 'fraud_label' in df.columns:
            try:
                fraud_counts = df['fraud_label'].value_counts()
                total_transactions = len(df)
                stats['fraud_distribution'] = {
                    'counts': fraud_counts.to_dict(),
                    'percentages': {
                        str(k): (v / total_transactions) * 100 
                        for k, v in fraud_counts.items()
                    },
                    'fraud_rate': (fraud_counts.get(1, 0) / total_transactions) * 100
                }
            except Exception as e:
                logger.warning(f"Error calculating fraud distribution: {e}")
                stats['fraud_distribution'] = {'error': str(e)}
        
        # Transaction uniqueness
        if 'transaction_id' in df.columns:
            try:
                unique_transactions = df['transaction_id'].nunique()
                duplicate_transactions = len(df) - unique_transactions
                stats['transaction_uniqueness'] = {
                    'unique_transactions': unique_transactions,
                    'duplicate_transactions': duplicate_transactions,
                    'duplicate_percentage': (duplicate_transactions / len(df)) * 100
                }
            except Exception as e:
                logger.warning(f"Error calculating transaction uniqueness: {e}")
                stats['transaction_uniqueness'] = {'error': str(e)}
        
        # Geographic diversity
        try:
            geographic_stats = {}
            if 'exporter_country' in df.columns:
                geographic_stats['unique_exporter_countries'] = df['exporter_country'].nunique()
                geographic_stats['top_exporter_countries'] = df['exporter_country'].value_counts().head(5).to_dict()
            
            if 'importer_country' in df.columns:
                geographic_stats['unique_importer_countries'] = df['importer_country'].nunique()
                geographic_stats['top_importer_countries'] = df['importer_country'].value_counts().head(5).to_dict()
            
            stats['geographic_diversity'] = geographic_stats
        except Exception as e:
            logger.warning(f"Error calculating geographic diversity: {e}")
            stats['geographic_diversity'] = {'error': str(e)}
        
        # Product diversity
        if 'product' in df.columns:
            try:
                stats['product_diversity'] = {
                    'unique_products': df['product'].nunique(),
                    'top_products': df['product'].value_counts().head(5).to_dict()
                }
            except Exception as e:
                logger.warning(f"Error calculating product diversity: {e}")
                stats['product_diversity'] = {'error': str(e)}
        
        # Trade value statistics
        if 'trade_value' in df.columns:
            try:
                trade_values = df['trade_value'].dropna()
                if len(trade_values) > 0:
                    stats['trade_value_stats'] = {
                        'total': float(trade_values.sum()),
                        'mean': float(trade_values.mean()),
                        'median': float(trade_values.median()),
                        'std': float(trade_values.std()),
                        'min': float(trade_values.min()),
                        'max': float(trade_values.max()),
                        'q25': float(trade_values.quantile(0.25)),
                        'q75': float(trade_values.quantile(0.75))
                    }
                else:
                    stats['trade_value_stats'] = {'error': 'No valid trade values found'}
            except Exception as e:
                logger.warning(f"Error calculating trade value statistics: {e}")
                stats['trade_value_stats'] = {'error': str(e)}
        
        # Risk indicators summary
        try:
            risk_stats = {}
            
            if 'company_risk_score' in df.columns:
                risk_scores = df['company_risk_score'].dropna()
                if len(risk_scores) > 0:
                    risk_stats['company_risk'] = {
                        'mean': float(risk_scores.mean()),
                        'high_risk_count': int((risk_scores > 0.8).sum()),
                        'high_risk_percentage': float((risk_scores > 0.8).mean() * 100)
                    }
            
            if 'route_anomaly' in df.columns:
                route_anomalies = df['route_anomaly'].dropna()
                if len(route_anomalies) > 0:
                    risk_stats['route_anomalies'] = {
                        'count': int(route_anomalies.sum()),
                        'percentage': float(route_anomalies.mean() * 100)
                    }
            
            if 'price_deviation' in df.columns:
                price_deviations = df['price_deviation'].dropna()
                if len(price_deviations) > 0:
                    risk_stats['price_deviations'] = {
                        'mean_deviation': float(price_deviations.mean()),
                        'high_deviation_count': int((abs(price_deviations) > 0.5).sum()),
                        'high_deviation_percentage': float((abs(price_deviations) > 0.5).mean() * 100)
                    }
            
            stats['risk_indicators'] = risk_stats
        except Exception as e:
            logger.warning(f"Error calculating risk indicators: {e}")
            stats['risk_indicators'] = {'error': str(e)}
        
        logger.debug("Dataset statistics calculated successfully")
        return stats
        
    except Exception as e:
        error_msg = f"Error calculating dataset statistics: {e}"
        logger.error(error_msg, exc_info=True)
        return {
            'error': error_msg,
            'basic_info': {
                'total_rows': len(df) if df is not None else 0,
                'total_columns': len(df.columns) if df is not None else 0
            }
        }

def validate_dataset_health(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform comprehensive dataset health check with detailed reporting.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        
    Returns:
        dict: Health check results with recommendations
    """
    logger.info("Performing comprehensive dataset health check")
    
    health_report = {
        'overall_health': 'UNKNOWN',
        'issues': [],
        'warnings': [],
        'recommendations': [],
        'metrics': {}
    }
    
    try:
        # Basic health metrics
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        missing_percentage = (missing_cells / total_cells) * 100 if total_cells > 0 else 0
        
        health_report['metrics'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_percentage': missing_percentage,
            'duplicate_percentage': (df.duplicated().sum() / len(df)) * 100 if len(df) > 0 else 0
        }
        
        # Assess overall health
        issues_count = 0
        warnings_count = 0
        
        # Check for critical issues
        if len(df) == 0:
            health_report['issues'].append("Dataset is empty")
            issues_count += 1
        
        if missing_percentage > 20:
            health_report['issues'].append(f"High missing data rate: {missing_percentage:.1f}%")
            issues_count += 1
        elif missing_percentage > 10:
            health_report['warnings'].append(f"Moderate missing data rate: {missing_percentage:.1f}%")
            warnings_count += 1
        
        # Check for required columns
        missing_required = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_required:
            health_report['issues'].append(f"Missing required columns: {missing_required}")
            issues_count += 1
        
        # Check data types
        if 'date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['date']):
            health_report['warnings'].append("Date column is not in datetime format")
            warnings_count += 1
        
        # Check for duplicates
        duplicate_percentage = health_report['metrics']['duplicate_percentage']
        if duplicate_percentage > 5:
            health_report['issues'].append(f"High duplicate rate: {duplicate_percentage:.1f}%")
            issues_count += 1
        elif duplicate_percentage > 1:
            health_report['warnings'].append(f"Moderate duplicate rate: {duplicate_percentage:.1f}%")
            warnings_count += 1
        
        # Generate recommendations
        if missing_percentage > 0:
            health_report['recommendations'].append("Consider data imputation strategies for missing values")
        
        if duplicate_percentage > 0:
            health_report['recommendations'].append("Review and remove duplicate records")
        
        if issues_count == 0 and warnings_count == 0:
            health_report['overall_health'] = 'EXCELLENT'
        elif issues_count == 0 and warnings_count <= 2:
            health_report['overall_health'] = 'GOOD'
        elif issues_count <= 1:
            health_report['overall_health'] = 'FAIR'
        else:
            health_report['overall_health'] = 'POOR'
        
        logger.info(f"Dataset health check completed. Overall health: {health_report['overall_health']}")
        
        return health_report
        
    except Exception as e:
        error_msg = f"Error during dataset health check: {e}"
        logger.error(error_msg, exc_info=True)
        health_report['overall_health'] = 'ERROR'
        health_report['issues'].append(error_msg)
        return health_report

def log_data_loading_summary(file_path: str, df: pd.DataFrame, processing_time: float) -> None:
    """
    Log a comprehensive summary of the data loading operation.
    
    Args:
        file_path (str): Path to the loaded file
        df (pd.DataFrame): Loaded DataFrame
        processing_time (float): Time taken to process the data
    """
    try:
        logger.info("=" * 60)
        logger.info("DATA LOADING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"File: {file_path}")
        logger.info(f"Processing Time: {processing_time:.2f} seconds")
        logger.info(f"Dataset Shape: {df.shape}")
        logger.info(f"Memory Usage: {df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB")
        
        # Health check
        health = validate_dataset_health(df)
        logger.info(f"Overall Health: {health['overall_health']}")
        
        if health['issues']:
            logger.warning(f"Issues Found: {len(health['issues'])}")
            for issue in health['issues']:
                logger.warning(f"  - {issue}")
        
        if health['warnings']:
            logger.info(f"Warnings: {len(health['warnings'])}")
            for warning in health['warnings']:
                logger.info(f"  - {warning}")
        
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error generating data loading summary: {e}")

# Utility function for safe file operations
def ensure_directory_exists(file_path: str) -> None:
    """
    Ensure the directory for a file path exists.
    
    Args:
        file_path (str): File path to check
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            raise

if __name__ == "__main__":
    # Test the enhanced data loader with comprehensive error handling and logging
    import time
    
    test_file_path = "../data/trinetra_trade_fraud_dataset_1000_rows_complex.csv"
    
    try:
        logger.info("Starting data loader test")
        start_time = time.time()
        
        # Load dataset with enhanced error handling
        df = load_dataset(test_file_path)
        
        processing_time = time.time() - start_time
        
        # Log comprehensive summary
        log_data_loading_summary(test_file_path, df, processing_time)
        
        # Display sample data
        print(f"\nSample data preview:")
        print(df.head())
        
        # Display column info
        print(f"\nColumn information:")
        print(df.dtypes)
        
        logger.info("Data loader test completed successfully")
        
    except (FileNotFoundError, SchemaValidationError, DataQualityError, DataLoaderError) as e:
        logger.error(f"Data loader test failed: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during data loader test: {e}", exc_info=True)
        print(f"Unexpected error: {e}")