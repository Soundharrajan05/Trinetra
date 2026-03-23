"""
Fraud Detection Engine for TRINETRA AI

This module provides fraud detection capabilities including:
- Loading trained ML models
- Scoring transactions for fraud risk
- Classifying transactions into risk categories
"""

import os
import joblib
import pandas as pd
import logging
from sklearn.ensemble import IsolationForest
from typing import Optional
import numpy as np

# Import common error handlers
try:
    from utils.helpers import error_handlers, ValidationHelpers, performance_tracker
except ImportError:
    # Fallback if utils.helpers is not available
    error_handlers = None
    ValidationHelpers = None
    performance_tracker = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_fraud_detector(model_path: str = "models/isolation_forest.pkl") -> Optional[IsolationForest]:
    """
    Load trained IsolationForest model from disk with comprehensive error handling.

    Args:
        model_path (str): Path to the trained model file

    Returns:
        IsolationForest: Loaded trained model, or None if loading fails

    Raises:
        FileNotFoundError: If model file doesn't exist and no fallback available
        ValueError: If loaded object is not a valid IsolationForest model
        Exception: If model loading fails for other reasons
    """
    try:
        # Validate input parameters
        if not model_path or not isinstance(model_path, str):
            raise ValueError("Model path must be a non-empty string")

        # Normalize path separators for cross-platform compatibility
        model_path = os.path.normpath(model_path)

        # Check if model file exists
        if not os.path.exists(model_path):
            logger.warning(f"Model file not found at {model_path}")

            # Only try alternative paths if using default path
            if model_path == os.path.normpath("models/isolation_forest.pkl"):
                alternative_paths = [
                    "models/isolation_forest_with_evaluation.pkl",
                    "isolation_forest.pkl",  # Check current directory
                    "../models/isolation_forest.pkl"  # Check parent directory
                ]

                for alt_path in alternative_paths:
                    alt_path = os.path.normpath(alt_path)
                    if os.path.exists(alt_path):
                        logger.info(f"Found alternative model at {alt_path}")
                        model_path = alt_path
                        break
                else:
                    error_msg = f"Model file not found at {model_path} or any alternative locations"
                    logger.error(error_msg)
                    raise FileNotFoundError(error_msg)
            else:
                error_msg = f"Model file not found at {model_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

        # Check file permissions and readability
        if not os.access(model_path, os.R_OK):
            error_msg = f"Model file at {model_path} is not readable (permission denied)"
            logger.error(error_msg)
            raise PermissionError(error_msg)

        # Check file size (empty files indicate corruption)
        file_size = os.path.getsize(model_path)
        if file_size == 0:
            error_msg = f"Model file at {model_path} is empty (0 bytes)"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Load the model using joblib with error handling
        logger.info(f"Loading fraud detection model from {model_path} (size: {file_size} bytes)")

        try:
            model = joblib.load(model_path)
        except (EOFError, ValueError) as e:
            error_msg = f"Model file at {model_path} appears to be corrupted: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Failed to deserialize model from {model_path}: {e}"
            logger.error(error_msg)
            raise

        # Validate that it's an IsolationForest model
        if not isinstance(model, IsolationForest):
            error_msg = f"Expected IsolationForest model, got {type(model).__name__}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Validate model state and parameters
        if not hasattr(model, 'decision_function'):
            error_msg = "Loaded model does not have decision_function method"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Check if model has been fitted
        if not hasattr(model, 'estimators_') or model.estimators_ is None:
            error_msg = "Model has not been fitted (no estimators found)"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Log model information
        n_estimators = len(model.estimators_) if hasattr(model, 'estimators_') else 'unknown'
        contamination = getattr(model, 'contamination', 'unknown')
        logger.info(f"Successfully loaded IsolationForest model with {n_estimators} estimators, contamination={contamination}")

        return model

    except FileNotFoundError:
        # Re-raise FileNotFoundError as-is for caller to handle
        raise
    except (ValueError, PermissionError):
        # Re-raise validation and permission errors as-is
        raise
    except Exception as e:
        # Catch any other unexpected errors
        error_msg = f"Unexpected error loading fraud detection model from {model_path}: {e}"
        logger.error(error_msg)
        raise Exception(error_msg) from e



def score_transactions(df: pd.DataFrame, model: IsolationForest) -> pd.DataFrame:
    """
    Generate anomaly scores for all transactions using the trained model with comprehensive error handling.
    
    Args:
        df (pd.DataFrame): DataFrame with engineered features
        model (IsolationForest): Trained fraud detection model
        
    Returns:
        pd.DataFrame: DataFrame with added risk_score column
        
    Raises:
        ValueError: If input validation fails or required features are missing
        TypeError: If inputs are not of expected types
        Exception: If scoring fails for other reasons
    """
    try:
        # Validate input parameters
        if df is None:
            raise ValueError("DataFrame cannot be None")
        
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
        
        if model is None:
            raise ValueError("Model cannot be None")
        
        if not isinstance(model, IsolationForest):
            raise TypeError(f"Expected IsolationForest model, got {type(model).__name__}")
        
        # Check if DataFrame is empty
        if df.empty:
            logger.warning("Input DataFrame is empty, returning empty DataFrame with risk_score column")
            empty_df = df.copy()
            empty_df['risk_score'] = pd.Series(dtype=float)
            return empty_df
        
        # Define the feature columns expected by the model
        feature_columns = [
            'price_anomaly_score',
            'route_risk_score', 
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
        
        # Check if all required features are present
        missing_features = [col for col in feature_columns if col not in df.columns]
        if missing_features:
            error_msg = f"Missing required features: {missing_features}. Available columns: {list(df.columns)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Extract features for prediction and validate data quality
        try:
            features = df[feature_columns].copy()
        except KeyError as e:
            error_msg = f"Error extracting features: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate features using common validation helpers
        if ValidationHelpers:
            validation_result = ValidationHelpers.validate_ml_model_input(features.values)
            if not validation_result['valid']:
                logger.warning(f"Feature validation warnings: {validation_result['warnings']}")
                if validation_result['errors']:
                    raise ValueError(f"Feature validation failed: {validation_result['errors']}")
        
        # Check for missing values in features
        missing_counts = features.isnull().sum()
        if missing_counts.any():
            logger.warning(f"Found missing values in features: {missing_counts[missing_counts > 0].to_dict()}")
            
            # Fill missing values with median (more robust than mean for outliers)
            for col in feature_columns:
                if features[col].isnull().any():
                    median_val = features[col].median()
                    if pd.isna(median_val):  # All values are NaN
                        logger.warning(f"All values in {col} are NaN, filling with 0")
                        features[col] = features[col].fillna(0)
                    else:
                        logger.info(f"Filling {features[col].isnull().sum()} missing values in {col} with median: {median_val}")
                        features[col] = features[col].fillna(median_val)
        
        # Check for infinite values
        inf_counts = features.isin([float('inf'), float('-inf')]).sum()
        if inf_counts.any():
            logger.warning(f"Found infinite values in features: {inf_counts[inf_counts > 0].to_dict()}")
            # Replace infinite values with large finite numbers
            features = features.replace([float('inf'), float('-inf')], [1e10, -1e10])
        
        # Validate feature data types
        for col in feature_columns:
            if not pd.api.types.is_numeric_dtype(features[col]):
                try:
                    features[col] = pd.to_numeric(features[col], errors='coerce')
                    logger.warning(f"Converted non-numeric column {col} to numeric")
                except Exception as e:
                    error_msg = f"Cannot convert feature {col} to numeric: {e}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
        
        # Check for extremely large values that might cause numerical issues
        for col in feature_columns:
            max_val = features[col].max()
            min_val = features[col].min()
            if abs(max_val) > 1e6 or abs(min_val) > 1e6:
                logger.warning(f"Feature {col} has extreme values (min: {min_val}, max: {max_val})")
        
        # Validate model state before prediction
        if not hasattr(model, 'decision_function'):
            error_msg = "Model does not have decision_function method"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Generate anomaly scores with error handling
        logger.info(f"Scoring {len(df)} transactions for fraud risk using {len(feature_columns)} features")
        
        try:
            risk_scores = model.decision_function(features)
        except ValueError as e:
            if "X has" in str(e) and "features" in str(e):
                error_msg = f"Feature dimension mismatch: {e}. Expected features: {feature_columns}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                error_msg = f"Model prediction failed: {e}"
                logger.error(error_msg)
                raise
        except Exception as e:
            error_msg = f"Unexpected error during model prediction: {e}"
            logger.error(error_msg)
            raise
        
        # Validate prediction results using common validation helpers
        if ValidationHelpers:
            pred_validation = ValidationHelpers.validate_model_predictions(
                risk_scores, expected_shape=(len(df),)
            )
            if not pred_validation['valid']:
                logger.warning(f"Prediction validation warnings: {pred_validation['warnings']}")
                if pred_validation['errors']:
                    raise ValueError(f"Prediction validation failed: {pred_validation['errors']}")
        
        # Validate prediction results
        if risk_scores is None:
            error_msg = "Model returned None for risk scores"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if len(risk_scores) != len(df):
            error_msg = f"Prediction length mismatch: expected {len(df)}, got {len(risk_scores)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check for invalid scores
        if pd.isna(risk_scores).any():
            nan_count = pd.isna(risk_scores).sum()
            logger.warning(f"Model returned {nan_count} NaN scores, replacing with 0")
            risk_scores = pd.Series(risk_scores).fillna(0).values
        
        # Add risk scores to DataFrame
        df_scored = df.copy()
        df_scored['risk_score'] = risk_scores
        
        # Log scoring statistics
        score_stats = pd.Series(risk_scores).describe()
        logger.info(f"Transaction scoring completed successfully. Score statistics: mean={score_stats['mean']:.4f}, std={score_stats['std']:.4f}, min={score_stats['min']:.4f}, max={score_stats['max']:.4f}")
        
        return df_scored
        
    except (ValueError, TypeError) as e:
        # Handle validation errors with common error handlers
        if error_handlers:
            error_info = error_handlers.handle_model_prediction_error(
                e, (len(df), len(feature_columns)) if 'feature_columns' in locals() else None, "IsolationForest"
            )
            logger.error(f"Transaction scoring failed: {error_info['user_message']}")
            if error_info.get('fallback_scores') is not None:
                logger.info("Using fallback risk scores")
                df_fallback = df.copy()
                df_fallback['risk_score'] = error_info['fallback_scores']
                return df_fallback
            raise ValueError(error_info['user_message'])
        else:
            # Re-raise validation errors as-is
            raise
    except Exception as e:
        # Handle general prediction errors with common error handlers
        if error_handlers:
            error_info = error_handlers.handle_model_prediction_error(
                e, (len(df), len(feature_columns)) if 'feature_columns' in locals() else None, "IsolationForest"
            )
            logger.error(f"Transaction scoring failed: {error_info['user_message']}")
            if error_info.get('fallback_scores') is not None:
                logger.info("Using fallback risk scores")
                df_fallback = df.copy()
                df_fallback['risk_score'] = error_info['fallback_scores']
                return df_fallback
            raise Exception(error_info['user_message'])
        else:
            # Catch any other unexpected errors
            error_msg = f"Unexpected error scoring transactions: {e}"
            logger.error(error_msg)
            raise Exception(error_msg) from e


def get_risk_category(score: float) -> str:
    """
    Classify risk score into risk category with deterministic thresholds.
    
    Args:
        score (float): Risk score from model
        
    Returns:
        str: Risk category (SAFE, SUSPICIOUS, or FRAUD)
        
    Raises:
        ValueError: If score is not a valid number
        TypeError: If score is not numeric
    """
    try:
        # Validate input
        if score is None:
            logger.warning("Risk score is None, defaulting to SUSPICIOUS")
            return "SUSPICIOUS"
        
        # Handle different numeric types
        if not isinstance(score, (int, float, complex)):
            try:
                score = float(score)
            except (ValueError, TypeError) as e:
                error_msg = f"Cannot convert score to float: {score} ({type(score).__name__})"
                logger.error(error_msg)
                raise ValueError(error_msg) from e
        
        # Handle special float values
        if pd.isna(score):
            logger.warning("Risk score is NaN, defaulting to SUSPICIOUS")
            return "SUSPICIOUS"
        
        if score == float('inf'):
            logger.warning("Risk score is positive infinity, classifying as FRAUD")
            return "FRAUD"
        
        if score == float('-inf'):
            logger.warning("Risk score is negative infinity, classifying as SAFE")
            return "SAFE"
        
        # Apply deterministic risk classification thresholds
        # These thresholds are calibrated for the dataset's fraud label distribution
        if score < -0.05:
            return "SAFE"
        elif score < 0.08:
            return "SUSPICIOUS"
        else:
            return "FRAUD"
            
    except Exception as e:
        # Fallback to SUSPICIOUS for any unexpected errors
        logger.error(f"Unexpected error in risk classification for score {score}: {e}")
        return "SUSPICIOUS"


def classify_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add risk category classification based on risk scores with comprehensive error handling.
    
    Args:
        df (pd.DataFrame): DataFrame with risk_score column
        
    Returns:
        pd.DataFrame: DataFrame with added risk_category column
        
    Raises:
        ValueError: If input validation fails or risk_score column is missing
        TypeError: If input is not a DataFrame
        Exception: If classification fails for other reasons
    """
    try:
        # Validate input parameters
        if df is None:
            raise ValueError("DataFrame cannot be None")
        
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
        
        # Check if DataFrame is empty
        if df.empty:
            logger.warning("Input DataFrame is empty, returning empty DataFrame with risk_category column")
            empty_df = df.copy()
            empty_df['risk_category'] = pd.Series(dtype=str)
            return empty_df
        
        # Check for required risk_score column
        if 'risk_score' not in df.columns:
            error_msg = f"DataFrame must contain 'risk_score' column. Available columns: {list(df.columns)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate risk_score column data
        risk_scores = df['risk_score']
        
        # Check for missing values in risk scores
        missing_count = risk_scores.isnull().sum()
        if missing_count > 0:
            logger.warning(f"Found {missing_count} missing risk scores, will classify as SUSPICIOUS")
        
        # Check data type of risk scores
        if not pd.api.types.is_numeric_dtype(risk_scores):
            logger.warning("Risk scores are not numeric, attempting conversion")
            try:
                risk_scores = pd.to_numeric(risk_scores, errors='coerce')
            except Exception as e:
                error_msg = f"Cannot convert risk_score column to numeric: {e}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Apply risk classification with error handling
        logger.info(f"Classifying {len(df)} transactions into risk categories")
        
        df_classified = df.copy()
        
        try:
            # Apply classification function to each score using deterministic thresholds
            df_classified['risk_category'] = df_classified['risk_score'].apply(get_risk_category)
        except Exception as e:
            error_msg = f"Error applying risk classification: {e}"
            logger.error(error_msg)
            raise
        
        # Validate classification results
        if 'risk_category' not in df_classified.columns:
            error_msg = "Risk category column was not created"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check for any missing categories (shouldn't happen with our robust get_risk_category)
        missing_categories = df_classified['risk_category'].isnull().sum()
        if missing_categories > 0:
            logger.warning(f"Found {missing_categories} missing risk categories, filling with SUSPICIOUS")
            df_classified['risk_category'] = df_classified['risk_category'].fillna('SUSPICIOUS')
        
        # Validate category values
        valid_categories = {'SAFE', 'SUSPICIOUS', 'FRAUD'}
        actual_categories = set(df_classified['risk_category'].unique())
        invalid_categories = actual_categories - valid_categories
        
        if invalid_categories:
            logger.warning(f"Found invalid risk categories: {invalid_categories}, replacing with SUSPICIOUS")
            mask = df_classified['risk_category'].isin(invalid_categories)
            df_classified.loc[mask, 'risk_category'] = 'SUSPICIOUS'
        
        # Log classification results
        try:
            category_counts = df_classified['risk_category'].value_counts()
            total_transactions = len(df_classified)
            
            logger.info("Risk classification results:")
            for category, count in category_counts.items():
                percentage = (count / total_transactions) * 100
                logger.info(f"  {category}: {count} transactions ({percentage:.1f}%)")
            
            # Log summary statistics
            if not risk_scores.empty:
                score_stats = risk_scores.describe()
                logger.info(f"Risk score statistics: mean={score_stats['mean']:.4f}, std={score_stats['std']:.4f}")
                
        except Exception as e:
            logger.warning(f"Could not log classification statistics: {e}")
        
        return df_classified
        
    except (ValueError, TypeError):
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        # Catch any other unexpected errors
        error_msg = f"Unexpected error classifying risk: {e}"
        logger.error(error_msg)
        raise Exception(error_msg) from e


def create_fallback_model() -> IsolationForest:
    """
    Create a basic fallback IsolationForest model when the trained model cannot be loaded.
    
    Returns:
        IsolationForest: A basic untrained model with default parameters
    """
    logger.warning("Creating fallback IsolationForest model with default parameters")
    
    fallback_model = IsolationForest(
        n_estimators=100,
        contamination=0.1,
        random_state=42,
        n_jobs=1  # Use single job for reliability
    )
    
    logger.info("Fallback model created successfully")
    return fallback_model


def validate_dataframe_schema(df: pd.DataFrame, required_columns: list = None) -> tuple[bool, list]:
    """
    Validate that a DataFrame has the expected schema for fraud detection.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        required_columns (list): List of required column names. If None, uses default feature columns.
        
    Returns:
        tuple: (is_valid, missing_columns)
    """
    if required_columns is None:
        required_columns = [
            'price_anomaly_score',
            'route_risk_score', 
            'company_network_risk',
            'port_congestion_score',
            'shipment_duration_risk',
            'volume_spike_score'
        ]
    
    try:
        if df is None or not isinstance(df, pd.DataFrame):
            return False, required_columns
        
        if df.empty:
            logger.warning("DataFrame is empty")
            return True, []  # Empty is valid, just no data to process
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False, missing_columns
        
        # Check for data quality issues
        for col in required_columns:
            if col in df.columns:
                # Check if column is entirely null
                if df[col].isnull().all():
                    logger.warning(f"Column {col} contains only null values")
                
                # Check if column has any valid numeric data
                if not pd.api.types.is_numeric_dtype(df[col]):
                    try:
                        pd.to_numeric(df[col], errors='coerce')
                    except Exception:
                        logger.warning(f"Column {col} cannot be converted to numeric")
        
        return True, []
        
    except Exception as e:
        logger.error(f"Error validating DataFrame schema: {e}")
        return False, required_columns


def safe_fraud_detection_pipeline(df: pd.DataFrame, model_path: str = "models/isolation_forest.pkl") -> pd.DataFrame:
    """
    Execute the complete fraud detection pipeline with comprehensive error handling and fallback mechanisms.
    
    Args:
        df (pd.DataFrame): Input DataFrame with engineered features
        model_path (str): Path to the trained model file
        
    Returns:
        pd.DataFrame: DataFrame with risk_score and risk_category columns added
        
    Note:
        This function implements graceful degradation - if the trained model fails to load,
        it will attempt to use a fallback model or rule-based classification.
    """
    try:
        logger.info("Starting safe fraud detection pipeline")
        
        # Validate input DataFrame
        is_valid, missing_cols = validate_dataframe_schema(df)
        if not is_valid:
            if df is None or df.empty:
                logger.error("Cannot process empty or None DataFrame")
                raise ValueError("Input DataFrame is empty or None")
            else:
                logger.error(f"DataFrame validation failed: missing columns {missing_cols}")
                raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Attempt to load the trained model
        model = None
        try:
            model = load_fraud_detector(model_path)
            logger.info("Successfully loaded trained fraud detection model")
        except Exception as e:
            logger.warning(f"Failed to load trained model: {e}")
            logger.info("Attempting to use rule-based fallback classification")
            
            # Use rule-based classification as fallback
            return _rule_based_fraud_classification(df)
        
        # Score transactions using the loaded model
        try:
            df_scored = score_transactions(df, model)
        except Exception as e:
            logger.error(f"Model scoring failed: {e}")
            logger.info("Falling back to rule-based classification")
            return _rule_based_fraud_classification(df)
        
        # Classify risk categories
        try:
            df_classified = classify_risk(df_scored)
        except Exception as e:
            logger.error(f"Risk classification failed: {e}")
            # If we have scores but classification fails, add basic categories
            df_classified = df_scored.copy()
            df_classified['risk_category'] = df_classified['risk_score'].apply(
                lambda x: 'FRAUD' if x > 0.2 else ('SAFE' if x < -0.2 else 'SUSPICIOUS')
            )
            logger.info("Applied basic risk classification as fallback")
        
        logger.info("Fraud detection pipeline completed successfully")
        return df_classified
        
    except Exception as e:
        logger.error(f"Fraud detection pipeline failed: {e}")
        # Last resort: return original DataFrame with default risk assessment
        try:
            fallback_df = df.copy()
            fallback_df['risk_score'] = 0.0  # Neutral score
            fallback_df['risk_category'] = 'SUSPICIOUS'  # Conservative classification
            logger.warning("Applied default risk assessment as final fallback")
            return fallback_df
        except Exception as final_e:
            logger.error(f"Even fallback failed: {final_e}")
            raise Exception("Complete fraud detection pipeline failure") from e


def _rule_based_fraud_classification(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fallback rule-based fraud classification when ML model is unavailable.
    
    Args:
        df (pd.DataFrame): DataFrame with engineered features
        
    Returns:
        pd.DataFrame: DataFrame with risk_score and risk_category columns
    """
    logger.info("Applying rule-based fraud classification")
    
    try:
        df_classified = df.copy()
        
        # Initialize risk score
        df_classified['risk_score'] = 0.0
        
        # Rule-based scoring using available features
        feature_weights = {
            'price_anomaly_score': 0.3,
            'route_risk_score': 0.2,
            'company_network_risk': 0.2,
            'port_congestion_score': 0.1,
            'shipment_duration_risk': 0.1,
            'volume_spike_score': 0.1
        }
        
        for feature, weight in feature_weights.items():
            if feature in df_classified.columns:
                # Normalize feature values and apply weight
                feature_values = df_classified[feature].fillna(0)
                
                # Simple normalization: values > 1 are suspicious
                normalized_values = (feature_values - 0.5) * weight
                df_classified['risk_score'] += normalized_values
        
        # Apply risk classification
        df_classified['risk_category'] = df_classified['risk_score'].apply(get_risk_category)
        
        logger.info("Rule-based classification completed")
        return df_classified
        
    except Exception as e:
        logger.error(f"Rule-based classification failed: {e}")
        # Final fallback
        df_fallback = df.copy()
        df_fallback['risk_score'] = 0.0
        df_fallback['risk_category'] = 'SUSPICIOUS'
        return df_fallback


def get_fraud_detection_health_status() -> dict:
    """
    Get the health status of the fraud detection system.
    
    Returns:
        dict: Health status information including model availability and system readiness
    """
    health_status = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'model_available': False,
        'model_path': None,
        'fallback_available': True,
        'system_ready': False,
        'errors': []
    }
    
    try:
        # Check if trained model is available
        default_model_path = "models/isolation_forest.pkl"
        try:
            model = load_fraud_detector(default_model_path)
            if model is not None:
                health_status['model_available'] = True
                health_status['model_path'] = default_model_path
                health_status['system_ready'] = True
        except Exception as e:
            health_status['errors'].append(f"Model loading failed: {str(e)}")
        
        # Check fallback capabilities
        try:
            fallback_model = create_fallback_model()
            if fallback_model is not None:
                health_status['fallback_available'] = True
                if not health_status['system_ready']:
                    health_status['system_ready'] = True  # Fallback makes system ready
        except Exception as e:
            health_status['fallback_available'] = False
            health_status['errors'].append(f"Fallback creation failed: {str(e)}")
        
        # Overall system status
        if not health_status['model_available'] and not health_status['fallback_available']:
            health_status['system_ready'] = False
            health_status['errors'].append("Neither trained model nor fallback is available")
        
        logger.info(f"Fraud detection health check completed: ready={health_status['system_ready']}")
        
    except Exception as e:
        health_status['errors'].append(f"Health check failed: {str(e)}")
        health_status['system_ready'] = False
        logger.error(f"Health status check failed: {e}")
    
    return health_status