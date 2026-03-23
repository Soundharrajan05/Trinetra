"""
ML Model Module for TRINETRA AI Trade Fraud Detection System

This module handles training and persistence of the IsolationForest anomaly detection model
for identifying fraudulent trade transactions.
"""

import pandas as pd
import numpy as np
import logging
import os
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Optional

# Configure logging
import time
from datetime import datetime
from pathlib import Path

# Import common error handlers
try:
    from utils.helpers import error_handlers, ValidationHelpers, performance_tracker
except ImportError:
    # Fallback if utils.helpers is not available
    error_handlers = None
    ValidationHelpers = None
    performance_tracker = None

def setup_model_logging():
    """Set up comprehensive logging configuration for the ML model."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging with both file and console handlers
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'trinetra_model.log'),
            logging.StreamHandler()
        ]
    )

# Initialize logging
setup_model_logging()
logger = logging.getLogger(__name__)

# Feature columns used for training
FEATURE_COLUMNS = [
    'price_anomaly_score',
    'route_risk_score', 
    'company_network_risk',
    'port_congestion_score',
    'shipment_duration_risk',
    'volume_spike_score'
]


def train_model(df: pd.DataFrame) -> IsolationForest:
    """
    Train IsolationForest on engineered features with comprehensive logging
    
    Args:
        df: DataFrame with engineered features
        
    Returns:
        Trained IsolationForest model
        
    Raises:
        ValueError: If required features are missing
        RuntimeError: If training fails
    """
    training_start_time = time.time()
    
    try:
        logger.info("=" * 60)
        logger.info("STARTING ML MODEL TRAINING SESSION")
        logger.info("=" * 60)
        logger.info(f"Training session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Validate that all required features are present
        missing_features = [col for col in FEATURE_COLUMNS if col not in df.columns]
        if missing_features:
            logger.error(f"Training failed: Missing required features: {missing_features}")
            raise ValueError(f"Missing required features: {missing_features}")
        
        logger.info(f"[OK] All required features present: {FEATURE_COLUMNS}")
        
        # Extract feature matrix
        X = df[FEATURE_COLUMNS].copy()
        logger.info(f"[OK] Feature matrix extracted: {X.shape[0]} samples × {X.shape[1]} features")
        
        # Handle any remaining NaN values
        nan_count = X.isnull().sum().sum()
        if nan_count > 0:
            logger.warning(f"Found {nan_count} NaN values in features, filling with median values")
            X = X.fillna(X.median())
            logger.info("[OK] NaN values handled successfully")
        else:
            logger.info("[OK] No NaN values found in feature matrix")
        
        # Log detailed feature statistics
        logger.info("FEATURE STATISTICS:")
        for feature in FEATURE_COLUMNS:
            feature_stats = X[feature].describe()
            logger.info(f"  {feature}:")
            logger.info(f"    Mean: {feature_stats['mean']:.4f}, Std: {feature_stats['std']:.4f}")
            logger.info(f"    Min: {feature_stats['min']:.4f}, Max: {feature_stats['max']:.4f}")
            logger.info(f"    25%: {feature_stats['25%']:.4f}, 75%: {feature_stats['75%']:.4f}")
        
        # Configure IsolationForest parameters
        model_params = {
            'n_estimators': 100,
            'contamination': 0.1,  # Expect ~10% fraud
            'random_state': 42,
            'n_jobs': -1
        }
        
        logger.info("MODEL CONFIGURATION:")
        for param, value in model_params.items():
            logger.info(f"  {param}: {value}")
        
        model = IsolationForest(**model_params)
        
        logger.info("Starting model training...")
        training_fit_start = time.time()
        
        # Train on engineered features
        model.fit(X)
        
        training_fit_time = time.time() - training_fit_start
        logger.info(f"[OK] Model training completed in {training_fit_time:.2f} seconds")
        
        # Log training performance with performance tracker
        if performance_tracker:
            performance_tracker.log_model_training(
                training_fit_time, "IsolationForest", len(FEATURE_COLUMNS)
            )
        
        # Log training results and model performance
        logger.info("TRAINING RESULTS:")
        logger.info(f"  Training samples: {len(X)}")
        logger.info(f"  Features used: {len(FEATURE_COLUMNS)}")
        logger.info(f"  Training time: {training_fit_time:.2f} seconds")
        logger.info(f"  Samples per second: {len(X) / training_fit_time:.2f}")
        
        # Get initial predictions for training set analysis
        logger.info("Analyzing training set predictions...")
        predictions = model.predict(X)
        anomaly_scores = model.decision_function(X)
        
        # Calculate training set statistics
        n_anomalies = np.sum(predictions == -1)
        n_normal = np.sum(predictions == 1)
        actual_contamination = n_anomalies / len(predictions)
        
        logger.info("TRAINING SET ANALYSIS:")
        logger.info(f"  Predicted anomalies: {n_anomalies} ({actual_contamination:.1%})")
        logger.info(f"  Predicted normal: {n_normal} ({(1-actual_contamination):.1%})")
        logger.info(f"  Expected contamination: {model_params['contamination']:.1%}")
        logger.info(f"  Actual contamination: {actual_contamination:.1%}")
        
        # Log anomaly score statistics
        logger.info("ANOMALY SCORE STATISTICS:")
        logger.info(f"  Score range: [{np.min(anomaly_scores):.4f}, {np.max(anomaly_scores):.4f}]")
        logger.info(f"  Score mean: {np.mean(anomaly_scores):.4f}")
        logger.info(f"  Score std: {np.std(anomaly_scores):.4f}")
        logger.info(f"  Score median: {np.median(anomaly_scores):.4f}")
        
        # Calculate and log feature importance
        try:
            logger.info("Calculating feature importance...")
            feature_importance = calculate_feature_importance(model, X)
            
            if 'feature_ranking' in feature_importance:
                logger.info("FEATURE IMPORTANCE RANKING:")
                for i, (feature, importance) in enumerate(feature_importance['feature_ranking'], 1):
                    logger.info(f"  {i}. {feature}: {importance:.4f}")
                
                most_important = feature_importance['most_important_feature']
                least_important = feature_importance['least_important_feature']
                logger.info(f"  Most important feature: {most_important}")
                logger.info(f"  Least important feature: {least_important}")
        except Exception as e:
            logger.warning(f"Could not calculate feature importance: {str(e)}")
        
        # Log model parameters and metadata
        logger.info("FINAL MODEL INFORMATION:")
        logger.info(f"  Model type: IsolationForest")
        logger.info(f"  Number of estimators: {model.n_estimators}")
        logger.info(f"  Contamination rate: {model.contamination}")
        logger.info(f"  Random state: {model.random_state}")
        logger.info(f"  Number of jobs: {model.n_jobs}")
        
        # Calculate total training time
        total_training_time = time.time() - training_start_time
        logger.info(f"  Total training session time: {total_training_time:.2f} seconds")
        
        # Save training report to file
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = log_dir / f"model_training_report_{timestamp}.txt"
            
            # Generate comprehensive training report
            training_report = generate_training_report(
                model, X, predictions, anomaly_scores, 
                training_fit_time, total_training_time, feature_importance
            )
            
            with open(report_file, 'w') as f:
                f.write(training_report)
            
            logger.info(f"[OK] Training report saved to: {report_file}")
            
        except Exception as e:
            logger.warning(f"Could not save training report: {str(e)}")
        
        logger.info("=" * 60)
        logger.info("MODEL TRAINING SESSION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
        # Return trained model
        return model
        
    except ValueError as e:
        # Handle validation errors with common error handlers
        if error_handlers:
            error_info = error_handlers.handle_model_training_error(
                e, "IsolationForest", len(FEATURE_COLUMNS) if 'FEATURE_COLUMNS' in globals() else 0
            )
            total_time = time.time() - training_start_time
            logger.error("=" * 60)
            logger.error("MODEL TRAINING SESSION FAILED")
            logger.error("=" * 60)
            logger.error(f"Training failed after {total_time:.2f} seconds")
            logger.error(f"Error: {error_info['user_message']}")
            logger.error("=" * 60)
            raise RuntimeError(error_info['user_message'])
        else:
            total_time = time.time() - training_start_time
            logger.error("=" * 60)
            logger.error("MODEL TRAINING SESSION FAILED")
            logger.error("=" * 60)
            logger.error(f"Training failed after {total_time:.2f} seconds")
            logger.error(f"Error: {str(e)}")
            logger.error("=" * 60)
            raise RuntimeError(f"Failed to train model: {str(e)}")
    except Exception as e:
        # Handle general training errors with common error handlers
        if error_handlers:
            error_info = error_handlers.handle_model_training_error(
                e, "IsolationForest", len(FEATURE_COLUMNS) if 'FEATURE_COLUMNS' in globals() else 0
            )
            total_time = time.time() - training_start_time
            logger.error("=" * 60)
            logger.error("MODEL TRAINING SESSION FAILED")
            logger.error("=" * 60)
            logger.error(f"Training failed after {total_time:.2f} seconds")
            logger.error(f"Error: {error_info['user_message']}")
            if error_info.get('recovery_actions'):
                logger.error(f"Suggested recovery actions: {error_info['recovery_actions']}")
            logger.error("=" * 60)
            raise RuntimeError(error_info['user_message'])
        else:
            total_time = time.time() - training_start_time
            logger.error("=" * 60)
            logger.error("MODEL TRAINING SESSION FAILED")
            logger.error("=" * 60)
            logger.error(f"Training failed after {total_time:.2f} seconds")
            logger.error(f"Error: {str(e)}")
            logger.error("=" * 60)
            raise RuntimeError(f"Failed to train model: {str(e)}")


def generate_training_report(model: IsolationForest, X: pd.DataFrame, predictions: np.ndarray, 
                           anomaly_scores: np.ndarray, training_time: float, total_time: float, 
                           feature_importance: dict) -> str:
    """
    Generate a comprehensive training report
    
    Args:
        model: Trained IsolationForest model
        X: Feature matrix used for training
        predictions: Model predictions on training set
        anomaly_scores: Anomaly scores for training set
        training_time: Time taken for model fitting
        total_time: Total training session time
        feature_importance: Feature importance analysis results
        
    Returns:
        Formatted training report as string
    """
    try:
        report = []
        report.append("=" * 80)
        report.append("TRINETRA AI - MODEL TRAINING REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Training Session Information
        report.append("TRAINING SESSION INFORMATION:")
        report.append(f"  Session Duration: {total_time:.2f} seconds")
        report.append(f"  Model Fitting Time: {training_time:.2f} seconds")
        report.append(f"  Overhead Time: {total_time - training_time:.2f} seconds")
        report.append(f"  Training Efficiency: {training_time/total_time:.1%}")
        report.append("")
        
        # Dataset Information
        report.append("DATASET INFORMATION:")
        report.append(f"  Training Samples: {len(X):,}")
        report.append(f"  Feature Count: {X.shape[1]}")
        report.append(f"  Samples per Second: {len(X) / training_time:.2f}")
        report.append(f"  Memory Usage: ~{X.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        report.append("")
        
        # Model Configuration
        report.append("MODEL CONFIGURATION:")
        report.append(f"  Algorithm: IsolationForest")
        report.append(f"  Number of Estimators: {model.n_estimators}")
        report.append(f"  Contamination Rate: {model.contamination}")
        report.append(f"  Random State: {model.random_state}")
        report.append(f"  Parallel Jobs: {model.n_jobs}")
        report.append("")
        
        # Feature Information
        report.append("FEATURE ANALYSIS:")
        report.append(f"  Features Used: {list(X.columns)}")
        report.append("")
        for feature in X.columns:
            stats = X[feature].describe()
            report.append(f"  {feature}:")
            report.append(f"    Range: [{stats['min']:.4f}, {stats['max']:.4f}]")
            report.append(f"    Mean ± Std: {stats['mean']:.4f} ± {stats['std']:.4f}")
            report.append(f"    Quartiles: Q1={stats['25%']:.4f}, Q2={stats['50%']:.4f}, Q3={stats['75%']:.4f}")
        report.append("")
        
        # Training Results
        n_anomalies = np.sum(predictions == -1)
        n_normal = np.sum(predictions == 1)
        actual_contamination = n_anomalies / len(predictions)
        
        report.append("TRAINING RESULTS:")
        report.append(f"  Predicted Anomalies: {n_anomalies:,} ({actual_contamination:.2%})")
        report.append(f"  Predicted Normal: {n_normal:,} ({(1-actual_contamination):.2%})")
        report.append(f"  Expected Contamination: {model.contamination:.2%}")
        report.append(f"  Actual Contamination: {actual_contamination:.2%}")
        report.append(f"  Contamination Difference: {abs(actual_contamination - model.contamination):.2%}")
        report.append("")
        
        # Anomaly Score Analysis
        report.append("ANOMALY SCORE ANALYSIS:")
        report.append(f"  Score Range: [{np.min(anomaly_scores):.4f}, {np.max(anomaly_scores):.4f}]")
        report.append(f"  Score Mean: {np.mean(anomaly_scores):.4f}")
        report.append(f"  Score Std: {np.std(anomaly_scores):.4f}")
        report.append(f"  Score Median: {np.median(anomaly_scores):.4f}")
        
        # Score percentiles
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        score_percentiles = np.percentile(anomaly_scores, percentiles)
        report.append("  Score Percentiles:")
        for p, score in zip(percentiles, score_percentiles):
            report.append(f"    {p}th percentile: {score:.4f}")
        report.append("")
        
        # Feature Importance
        if feature_importance and 'feature_ranking' in feature_importance:
            report.append("FEATURE IMPORTANCE RANKING:")
            for i, (feature, importance) in enumerate(feature_importance['feature_ranking'], 1):
                report.append(f"  {i:2d}. {feature:<25} {importance:.4f}")
            report.append("")
            report.append(f"  Most Important: {feature_importance.get('most_important_feature', 'N/A')}")
            report.append(f"  Least Important: {feature_importance.get('least_important_feature', 'N/A')}")
        else:
            report.append("FEATURE IMPORTANCE: Not available")
        report.append("")
        
        # Performance Metrics
        report.append("PERFORMANCE METRICS:")
        report.append(f"  Training Throughput: {len(X) / training_time:.2f} samples/second")
        report.append(f"  Memory Efficiency: {len(X) / (X.memory_usage(deep=True).sum() / 1024**2):.0f} samples/MB")
        report.append(f"  Time per Sample: {training_time / len(X) * 1000:.4f} ms")
        report.append("")
        
        # Model Quality Indicators
        report.append("MODEL QUALITY INDICATORS:")
        
        # Check if contamination rate is reasonable
        contamination_diff = abs(actual_contamination - model.contamination)
        if contamination_diff < 0.02:
            contamination_status = "[OK] Good"
        elif contamination_diff < 0.05:
            contamination_status = "[WARN] Acceptable"
        else:
            contamination_status = "[ERROR] Poor"
        report.append(f"  Contamination Accuracy: {contamination_status} (diff: {contamination_diff:.2%})")
        
        # Check score distribution
        score_range = np.max(anomaly_scores) - np.min(anomaly_scores)
        if score_range > 0.5:
            score_status = "[OK] Good separation"
        elif score_range > 0.2:
            score_status = "[WARN] Moderate separation"
        else:
            score_status = "[ERROR] Poor separation"
        report.append(f"  Score Separation: {score_status} (range: {score_range:.4f})")
        
        # Check training speed
        if training_time < 10:
            speed_status = "[OK] Fast"
        elif training_time < 30:
            speed_status = "[WARN] Moderate"
        else:
            speed_status = "[ERROR] Slow"
        report.append(f"  Training Speed: {speed_status} ({training_time:.2f}s)")
        report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS:")
        if contamination_diff > 0.05:
            report.append("  • Consider adjusting contamination parameter")
        if score_range < 0.2:
            report.append("  • Consider feature engineering or parameter tuning")
        if training_time > 30:
            report.append("  • Consider reducing n_estimators or using fewer features")
        if len(X) < 1000:
            report.append("  • Consider collecting more training data")
        
        report.append("")
        report.append("=" * 80)
        report.append("END OF TRAINING REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
        
    except Exception as e:
        logger.error(f"Training report generation failed: {str(e)}")
        return f"Error generating training report: {str(e)}"


def save_model(model: IsolationForest, path: str) -> None:
    """
    Persist model to disk using joblib with comprehensive logging
    
    Args:
        model: Trained IsolationForest model
        path: File path to save the model
        
    Raises:
        RuntimeError: If saving fails
    """
    try:
        save_start_time = time.time()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        logger.info(f"Saving model to: {path}")
        
        # Get model size estimate before saving
        import sys
        model_size_mb = sys.getsizeof(model) / 1024**2
        logger.info(f"Estimated model size: {model_size_mb:.2f} MB")
        
        # Save the model
        joblib.dump(model, path)
        
        save_time = time.time() - save_start_time
        
        # Verify the saved file
        if os.path.exists(path):
            file_size_mb = os.path.getsize(path) / 1024**2
            logger.info(f"[OK] Model saved successfully in {save_time:.2f} seconds")
            logger.info(f"[OK] Saved file size: {file_size_mb:.2f} MB")
            logger.info(f"[OK] Save location: {os.path.abspath(path)}")
        else:
            raise RuntimeError("Model file was not created")
        
    except Exception as e:
        logger.error(f"Failed to save model to {path}: {str(e)}")
        raise RuntimeError(f"Failed to save model: {str(e)}")


def load_model(path: str) -> IsolationForest:
    """
    Load trained model from disk with comprehensive logging
    
    Args:
        path: File path to load the model from
        
    Returns:
        Loaded IsolationForest model
        
    Raises:
        FileNotFoundError: If model file doesn't exist
        RuntimeError: If loading fails
    """
    try:
        load_start_time = time.time()
        
        if not os.path.exists(path):
            logger.error(f"Model file not found: {path}")
            raise FileNotFoundError(f"Model file not found: {path}")
        
        # Log file information
        file_size_mb = os.path.getsize(path) / 1024**2
        file_modified = datetime.fromtimestamp(os.path.getmtime(path))
        
        logger.info(f"Loading model from: {path}")
        logger.info(f"Model file size: {file_size_mb:.2f} MB")
        logger.info(f"Model last modified: {file_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load the model
        model = joblib.load(path)
        
        load_time = time.time() - load_start_time
        
        # Validate loaded model
        if not isinstance(model, IsolationForest):
            raise RuntimeError(f"Loaded object is not an IsolationForest model: {type(model)}")
        
        # Log model information
        logger.info(f"[OK] Model loaded successfully in {load_time:.2f} seconds")
        logger.info(f"[OK] Model type: {type(model).__name__}")
        logger.info(f"[OK] Model parameters:")
        logger.info(f"    n_estimators: {model.n_estimators}")
        logger.info(f"    contamination: {model.contamination}")
        logger.info(f"    random_state: {model.random_state}")
        
        # Check if model is fitted
        if hasattr(model, 'estimators_'):
            logger.info(f"[OK] Model is fitted with {len(model.estimators_)} estimators")
        else:
            logger.warning("[WARN] Model appears to be unfitted")
        
        return model
        
    except FileNotFoundError as e:
        # Handle file not found with common error handlers
        if error_handlers:
            error_info = error_handlers.handle_model_loading_error(e, path)
            logger.error(f"Model loading failed: {error_info['user_message']}")
            if error_info.get('can_retrain'):
                logger.info("Model can be retrained automatically")
            raise FileNotFoundError(error_info['user_message'])
        else:
            raise
    except Exception as e:
        # Handle general loading errors with common error handlers
        if error_handlers:
            error_info = error_handlers.handle_model_loading_error(e, path)
            logger.error(f"Model loading failed: {error_info['user_message']}")
            if error_info.get('suggested_actions'):
                logger.error(f"Suggested actions: {error_info['suggested_actions']}")
            raise RuntimeError(error_info['user_message'])
        else:
            logger.error(f"Failed to load model from {path}: {str(e)}")
            raise RuntimeError(f"Failed to load model: {str(e)}")


def get_model_info(model: IsolationForest) -> dict:
    """
    Get information about the trained model
    
    Args:
        model: Trained IsolationForest model
        
    Returns:
        Dictionary with model information
    """
    try:
        info = {
            'model_type': 'IsolationForest',
            'n_estimators': model.n_estimators,
            'contamination': model.contamination,
            'random_state': model.random_state,
            'n_jobs': model.n_jobs,
            'n_features': len(FEATURE_COLUMNS),
            'feature_columns': FEATURE_COLUMNS
        }
        
        # Add training-specific info if available
        if hasattr(model, 'estimators_'):
            info['n_trained_estimators'] = len(model.estimators_)
            
        return info
        
    except Exception as e:
        logger.error(f"Failed to get model info: {str(e)}")
        return {'error': str(e)}


def evaluate_model(model: IsolationForest, X: pd.DataFrame, y_true: Optional[pd.Series] = None) -> dict:
    """
    Evaluate the trained IsolationForest model with comprehensive metrics
    
    Args:
        model: Trained IsolationForest model
        X: Feature matrix used for evaluation
        y_true: Optional true labels (1 for normal, -1 for anomaly)
        
    Returns:
        Dictionary containing evaluation metrics
    """
    try:
        from sklearn.metrics import silhouette_score, classification_report, confusion_matrix
        from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
        import time
        
        logger.info("Starting model evaluation...")
        
        # Validate inputs
        if X.empty:
            raise ValueError("Feature matrix X cannot be empty")
        
        # Get anomaly scores and predictions
        start_time = time.time()
        anomaly_scores = model.decision_function(X)
        predictions = model.predict(X)
        prediction_time = time.time() - start_time
        
        # Initialize evaluation results
        evaluation_results = {
            'model_info': {
                'model_type': 'IsolationForest',
                'n_estimators': model.n_estimators,
                'contamination': model.contamination,
                'n_features': X.shape[1],
                'n_samples': X.shape[0]
            },
            'performance_metrics': {
                'prediction_time_seconds': round(prediction_time, 4),
                'predictions_per_second': round(X.shape[0] / prediction_time, 2)
            },
            'anomaly_analysis': {},
            'feature_analysis': {}
        }
        
        # Anomaly score statistics
        evaluation_results['anomaly_analysis'] = {
            'anomaly_score_mean': float(np.mean(anomaly_scores)),
            'anomaly_score_std': float(np.std(anomaly_scores)),
            'anomaly_score_min': float(np.min(anomaly_scores)),
            'anomaly_score_max': float(np.max(anomaly_scores)),
            'anomaly_score_median': float(np.median(anomaly_scores)),
            'predicted_anomalies': int(np.sum(predictions == -1)),
            'predicted_normal': int(np.sum(predictions == 1)),
            'actual_contamination_rate': float(np.sum(predictions == -1) / len(predictions))
        }
        
        # Calculate silhouette score for clustering quality
        try:
            # Convert predictions to 0/1 for silhouette score (needs at least 2 clusters)
            if len(np.unique(predictions)) > 1:
                silhouette_avg = silhouette_score(X, predictions)
                evaluation_results['anomaly_analysis']['silhouette_score'] = float(silhouette_avg)
            else:
                evaluation_results['anomaly_analysis']['silhouette_score'] = None
                logger.warning("Cannot calculate silhouette score: only one cluster predicted")
        except Exception as e:
            logger.warning(f"Could not calculate silhouette score: {str(e)}")
            evaluation_results['anomaly_analysis']['silhouette_score'] = None
        
        # Feature importance analysis (based on feature contribution to anomaly scores)
        try:
            feature_importance = calculate_feature_importance(model, X)
            evaluation_results['feature_analysis'] = feature_importance
        except Exception as e:
            logger.warning(f"Could not calculate feature importance: {str(e)}")
            evaluation_results['feature_analysis'] = {'error': str(e)}
        
        # If true labels are provided, calculate supervised metrics
        if y_true is not None:
            try:
                # Convert true labels to match model output format (-1 for anomaly, 1 for normal)
                if set(y_true.unique()).issubset({0, 1}):
                    # Convert 0/1 to -1/1 format
                    y_true_converted = y_true.map({0: 1, 1: -1})  # 0=normal=1, 1=anomaly=-1
                else:
                    y_true_converted = y_true
                
                supervised_metrics = calculate_supervised_metrics(predictions, y_true_converted)
                evaluation_results['supervised_metrics'] = supervised_metrics
                
            except Exception as e:
                logger.warning(f"Could not calculate supervised metrics: {str(e)}")
                evaluation_results['supervised_metrics'] = {'error': str(e)}
        
        logger.info("Model evaluation completed successfully")
        return evaluation_results
        
    except Exception as e:
        logger.error(f"Model evaluation failed: {str(e)}")
        raise RuntimeError(f"Failed to evaluate model: {str(e)}")



def evaluate_model(model: IsolationForest, X: pd.DataFrame, y_true: Optional[pd.Series] = None) -> dict:
    """
    Evaluate the trained IsolationForest model with comprehensive metrics

    Args:
        model: Trained IsolationForest model
        X: Feature matrix used for evaluation
        y_true: Optional true labels (1 for normal, -1 for anomaly)

    Returns:
        Dictionary containing evaluation metrics
    """
    try:
        from sklearn.metrics import silhouette_score, classification_report, confusion_matrix
        from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
        import time

        logger.info("Starting model evaluation...")

        # Validate inputs
        if X.empty:
            raise ValueError("Feature matrix X cannot be empty")

        # Get anomaly scores and predictions
        start_time = time.time()
        anomaly_scores = model.decision_function(X)
        predictions = model.predict(X)
        prediction_time = time.time() - start_time

        # Initialize evaluation results
        evaluation_results = {
            'model_info': {
                'model_type': 'IsolationForest',
                'n_estimators': model.n_estimators,
                'contamination': model.contamination,
                'n_features': X.shape[1],
                'n_samples': X.shape[0]
            },
            'performance_metrics': {
                'prediction_time_seconds': round(prediction_time, 4),
                'predictions_per_second': round(X.shape[0] / prediction_time, 2)
            },
            'anomaly_analysis': {},
            'feature_analysis': {}
        }

        # Anomaly score statistics
        evaluation_results['anomaly_analysis'] = {
            'anomaly_score_mean': float(np.mean(anomaly_scores)),
            'anomaly_score_std': float(np.std(anomaly_scores)),
            'anomaly_score_min': float(np.min(anomaly_scores)),
            'anomaly_score_max': float(np.max(anomaly_scores)),
            'anomaly_score_median': float(np.median(anomaly_scores)),
            'predicted_anomalies': int(np.sum(predictions == -1)),
            'predicted_normal': int(np.sum(predictions == 1)),
            'actual_contamination_rate': float(np.sum(predictions == -1) / len(predictions))
        }

        # Calculate silhouette score for clustering quality
        try:
            # Convert predictions to 0/1 for silhouette score (needs at least 2 clusters)
            if len(np.unique(predictions)) > 1:
                silhouette_avg = silhouette_score(X, predictions)
                evaluation_results['anomaly_analysis']['silhouette_score'] = float(silhouette_avg)
            else:
                evaluation_results['anomaly_analysis']['silhouette_score'] = None
                logger.warning("Cannot calculate silhouette score: only one cluster predicted")
        except Exception as e:
            logger.warning(f"Could not calculate silhouette score: {str(e)}")
            evaluation_results['anomaly_analysis']['silhouette_score'] = None

        # Feature importance analysis (based on feature contribution to anomaly scores)
        try:
            feature_importance = calculate_feature_importance(model, X)
            evaluation_results['feature_analysis'] = feature_importance
        except Exception as e:
            logger.warning(f"Could not calculate feature importance: {str(e)}")
            evaluation_results['feature_analysis'] = {'error': str(e)}

        # If true labels are provided, calculate supervised metrics
        if y_true is not None:
            try:
                # Convert true labels to match model output format (-1 for anomaly, 1 for normal)
                if set(y_true.unique()).issubset({0, 1}):
                    # Convert 0/1 to -1/1 format
                    y_true_converted = y_true.map({0: 1, 1: -1})  # 0=normal=1, 1=anomaly=-1
                else:
                    y_true_converted = y_true

                supervised_metrics = calculate_supervised_metrics(predictions, y_true_converted)
                evaluation_results['supervised_metrics'] = supervised_metrics

            except Exception as e:
                logger.warning(f"Could not calculate supervised metrics: {str(e)}")
                evaluation_results['supervised_metrics'] = {'error': str(e)}

        logger.info("Model evaluation completed successfully")
        return evaluation_results

    except Exception as e:
        logger.error(f"Model evaluation failed: {str(e)}")
        raise RuntimeError(f"Failed to evaluate model: {str(e)}")


def calculate_feature_importance(model: IsolationForest, X: pd.DataFrame) -> dict:
    """
    Calculate feature importance for IsolationForest model

    Args:
        model: Trained IsolationForest model
        X: Feature matrix

    Returns:
        Dictionary with feature importance metrics
    """
    try:
        # For IsolationForest, we can estimate feature importance by:
        # 1. Permutation importance (how much performance drops when feature is shuffled)
        # 2. Feature contribution to anomaly scores

        feature_names = X.columns.tolist()
        n_features = len(feature_names)

        # Get baseline anomaly scores
        baseline_scores = model.decision_function(X)
        baseline_mean = np.mean(baseline_scores)

        # Calculate permutation importance
        importance_scores = []

        for i, feature in enumerate(feature_names):
            # Create a copy of X and shuffle the feature
            X_permuted = X.copy()
            X_permuted.iloc[:, i] = np.random.permutation(X_permuted.iloc[:, i])

            # Get anomaly scores with permuted feature
            permuted_scores = model.decision_function(X_permuted)
            permuted_mean = np.mean(permuted_scores)

            # Importance is the change in mean anomaly score
            importance = abs(baseline_mean - permuted_mean)
            importance_scores.append(importance)

        # Normalize importance scores
        total_importance = sum(importance_scores)
        if total_importance > 0:
            normalized_importance = [score / total_importance for score in importance_scores]
        else:
            normalized_importance = [1.0 / n_features] * n_features

        # Create feature importance dictionary
        feature_importance = {
            'feature_importance_scores': dict(zip(feature_names, normalized_importance)),
            'feature_ranking': sorted(zip(feature_names, normalized_importance),
                                    key=lambda x: x[1], reverse=True),
            'most_important_feature': max(zip(feature_names, normalized_importance),
                                        key=lambda x: x[1])[0],
            'least_important_feature': min(zip(feature_names, normalized_importance),
                                         key=lambda x: x[1])[0]
        }

        return feature_importance

    except Exception as e:
        logger.error(f"Feature importance calculation failed: {str(e)}")
        return {'error': str(e)}


def calculate_supervised_metrics(predictions: np.ndarray, y_true: np.ndarray) -> dict:
    """
    Calculate supervised learning metrics when true labels are available

    Args:
        predictions: Model predictions (-1 for anomaly, 1 for normal)
        y_true: True labels (-1 for anomaly, 1 for normal)

    Returns:
        Dictionary with supervised metrics
    """
    try:
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            confusion_matrix, classification_report
        )

        # Calculate basic metrics
        accuracy = accuracy_score(y_true, predictions)

        # For binary classification with -1/1 labels, we need to specify pos_label
        precision = precision_score(y_true, predictions, pos_label=-1)  # -1 is anomaly (positive class)
        recall = recall_score(y_true, predictions, pos_label=-1)
        f1 = f1_score(y_true, predictions, pos_label=-1)

        # Confusion matrix
        cm = confusion_matrix(y_true, predictions, labels=[1, -1])  # [normal, anomaly]
        tn, fp, fn, tp = cm.ravel()

        # Additional metrics
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        false_negative_rate = fn / (fn + tp) if (fn + tp) > 0 else 0

        supervised_metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'specificity': float(specificity),
            'false_positive_rate': float(false_positive_rate),
            'false_negative_rate': float(false_negative_rate),
            'confusion_matrix': {
                'true_negative': int(tn),
                'false_positive': int(fp),
                'false_negative': int(fn),
                'true_positive': int(tp)
            },
            'support': {
                'normal_samples': int(np.sum(y_true == 1)),
                'anomaly_samples': int(np.sum(y_true == -1))
            }
        }

        return supervised_metrics

    except Exception as e:
        logger.error(f"Supervised metrics calculation failed: {str(e)}")
        return {'error': str(e)}


def generate_model_report(model: IsolationForest, X: pd.DataFrame, y_true: Optional[pd.Series] = None) -> str:
    """
    Generate a comprehensive text report of model evaluation

    Args:
        model: Trained IsolationForest model
        X: Feature matrix
        y_true: Optional true labels

    Returns:
        Formatted text report
    """
    try:
        # Get evaluation metrics
        evaluation = evaluate_model(model, X, y_true)

        # Generate report
        report = []
        report.append("=" * 60)
        report.append("TRINETRA AI - MODEL EVALUATION REPORT")
        report.append("=" * 60)
        report.append("")

        # Model Information
        model_info = evaluation['model_info']
        report.append("MODEL INFORMATION:")
        report.append(f"  Model Type: {model_info['model_type']}")
        report.append(f"  Number of Estimators: {model_info['n_estimators']}")
        report.append(f"  Contamination Rate: {model_info['contamination']}")
        report.append(f"  Features: {model_info['n_features']}")
        report.append(f"  Training Samples: {model_info['n_samples']}")
        report.append("")

        # Performance Metrics
        perf = evaluation['performance_metrics']
        report.append("PERFORMANCE METRICS:")
        report.append(f"  Prediction Time: {perf['prediction_time_seconds']} seconds")
        report.append(f"  Throughput: {perf['predictions_per_second']} predictions/second")
        report.append("")

        # Anomaly Analysis
        anomaly = evaluation['anomaly_analysis']
        report.append("ANOMALY DETECTION ANALYSIS:")
        report.append(f"  Predicted Anomalies: {anomaly['predicted_anomalies']}")
        report.append(f"  Predicted Normal: {anomaly['predicted_normal']}")
        report.append(f"  Actual Contamination Rate: {anomaly['actual_contamination_rate']:.3f}")
        report.append(f"  Expected Contamination Rate: {model_info['contamination']}")
        report.append(f"  Anomaly Score Range: [{anomaly['anomaly_score_min']:.3f}, {anomaly['anomaly_score_max']:.3f}]")
        report.append(f"  Anomaly Score Mean: {anomaly['anomaly_score_mean']:.3f}")
        report.append(f"  Anomaly Score Std: {anomaly['anomaly_score_std']:.3f}")
        if anomaly.get('silhouette_score') is not None:
            report.append(f"  Silhouette Score: {anomaly['silhouette_score']:.3f}")
        report.append("")

        # Feature Analysis
        if 'feature_importance_scores' in evaluation['feature_analysis']:
            feature_analysis = evaluation['feature_analysis']
            report.append("FEATURE IMPORTANCE ANALYSIS:")
            report.append(f"  Most Important Feature: {feature_analysis['most_important_feature']}")
            report.append(f"  Least Important Feature: {feature_analysis['least_important_feature']}")
            report.append("  Feature Rankings:")
            for feature, importance in feature_analysis['feature_ranking']:
                report.append(f"    {feature}: {importance:.3f}")
            report.append("")

        # Supervised Metrics (if available)
        if 'supervised_metrics' in evaluation and 'error' not in evaluation['supervised_metrics']:
            supervised = evaluation['supervised_metrics']
            report.append("SUPERVISED LEARNING METRICS:")
            report.append(f"  Accuracy: {supervised['accuracy']:.3f}")
            report.append(f"  Precision: {supervised['precision']:.3f}")
            report.append(f"  Recall: {supervised['recall']:.3f}")
            report.append(f"  F1-Score: {supervised['f1_score']:.3f}")
            report.append(f"  Specificity: {supervised['specificity']:.3f}")
            report.append("")
            report.append("  Confusion Matrix:")
            cm = supervised['confusion_matrix']
            report.append(f"    True Negative: {cm['true_negative']}")
            report.append(f"    False Positive: {cm['false_positive']}")
            report.append(f"    False Negative: {cm['false_negative']}")
            report.append(f"    True Positive: {cm['true_positive']}")
            report.append("")

        report.append("=" * 60)

        return "\n".join(report)

    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        return f"Error generating report: {str(e)}"


def calculate_feature_importance(model: IsolationForest, X: pd.DataFrame) -> dict:
    """
    Calculate feature importance for IsolationForest model
    
    Args:
        model: Trained IsolationForest model
        X: Feature matrix
        
    Returns:
        Dictionary with feature importance metrics
    """
    try:
        # For IsolationForest, we can estimate feature importance by:
        # 1. Permutation importance (how much performance drops when feature is shuffled)
        # 2. Feature contribution to anomaly scores
        
        feature_names = X.columns.tolist()
        n_features = len(feature_names)
        
        # Get baseline anomaly scores
        baseline_scores = model.decision_function(X)
        baseline_mean = np.mean(baseline_scores)
        
        # Calculate permutation importance
        importance_scores = []
        
        for i, feature in enumerate(feature_names):
            # Create a copy of X and shuffle the feature
            X_permuted = X.copy()
            X_permuted.iloc[:, i] = np.random.permutation(X_permuted.iloc[:, i])
            
            # Get anomaly scores with permuted feature
            permuted_scores = model.decision_function(X_permuted)
            permuted_mean = np.mean(permuted_scores)
            
            # Importance is the change in mean anomaly score
            importance = abs(baseline_mean - permuted_mean)
            importance_scores.append(importance)
        
        # Normalize importance scores
        total_importance = sum(importance_scores)
        if total_importance > 0:
            normalized_importance = [score / total_importance for score in importance_scores]
        else:
            normalized_importance = [1.0 / n_features] * n_features
        
        # Create feature importance dictionary
        feature_importance = {
            'feature_importance_scores': dict(zip(feature_names, normalized_importance)),
            'feature_ranking': sorted(zip(feature_names, normalized_importance), 
                                    key=lambda x: x[1], reverse=True),
            'most_important_feature': max(zip(feature_names, normalized_importance), 
                                        key=lambda x: x[1])[0],
            'least_important_feature': min(zip(feature_names, normalized_importance), 
                                         key=lambda x: x[1])[0]
        }
        
        return feature_importance
        
    except Exception as e:
        logger.error(f"Feature importance calculation failed: {str(e)}")
        return {'error': str(e)}


def calculate_supervised_metrics(predictions: np.ndarray, y_true: np.ndarray) -> dict:
    """
    Calculate supervised learning metrics when true labels are available
    
    Args:
        predictions: Model predictions (-1 for anomaly, 1 for normal)
        y_true: True labels (-1 for anomaly, 1 for normal)
        
    Returns:
        Dictionary with supervised metrics
    """
    try:
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            confusion_matrix, classification_report
        )
        
        # Calculate basic metrics
        accuracy = accuracy_score(y_true, predictions)
        
        # For binary classification with -1/1 labels, we need to specify pos_label
        precision = precision_score(y_true, predictions, pos_label=-1)  # -1 is anomaly (positive class)
        recall = recall_score(y_true, predictions, pos_label=-1)
        f1 = f1_score(y_true, predictions, pos_label=-1)
        
        # Confusion matrix
        cm = confusion_matrix(y_true, predictions, labels=[1, -1])  # [normal, anomaly]
        tn, fp, fn, tp = cm.ravel()
        
        # Additional metrics
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        false_negative_rate = fn / (fn + tp) if (fn + tp) > 0 else 0
        
        supervised_metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'specificity': float(specificity),
            'false_positive_rate': float(false_positive_rate),
            'false_negative_rate': float(false_negative_rate),
            'confusion_matrix': {
                'true_negative': int(tn),
                'false_positive': int(fp),
                'false_negative': int(fn),
                'true_positive': int(tp)
            },
            'support': {
                'normal_samples': int(np.sum(y_true == 1)),
                'anomaly_samples': int(np.sum(y_true == -1))
            }
        }
        
        return supervised_metrics
        
    except Exception as e:
        logger.error(f"Supervised metrics calculation failed: {str(e)}")
        return {'error': str(e)}


def generate_model_report(model: IsolationForest, X: pd.DataFrame, y_true: Optional[pd.Series] = None) -> str:
    """
    Generate a comprehensive text report of model evaluation
    
    Args:
        model: Trained IsolationForest model
        X: Feature matrix
        y_true: Optional true labels
        
    Returns:
        Formatted text report
    """
    try:
        # Get evaluation metrics
        evaluation = evaluate_model(model, X, y_true)
        
        # Generate report
        report = []
        report.append("=" * 60)
        report.append("TRINETRA AI - MODEL EVALUATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Model Information
        model_info = evaluation['model_info']
        report.append("MODEL INFORMATION:")
        report.append(f"  Model Type: {model_info['model_type']}")
        report.append(f"  Number of Estimators: {model_info['n_estimators']}")
        report.append(f"  Contamination Rate: {model_info['contamination']}")
        report.append(f"  Features: {model_info['n_features']}")
        report.append(f"  Training Samples: {model_info['n_samples']}")
        report.append("")
        
        # Performance Metrics
        perf = evaluation['performance_metrics']
        report.append("PERFORMANCE METRICS:")
        report.append(f"  Prediction Time: {perf['prediction_time_seconds']} seconds")
        report.append(f"  Throughput: {perf['predictions_per_second']} predictions/second")
        report.append("")
        
        # Anomaly Analysis
        anomaly = evaluation['anomaly_analysis']
        report.append("ANOMALY DETECTION ANALYSIS:")
        report.append(f"  Predicted Anomalies: {anomaly['predicted_anomalies']}")
        report.append(f"  Predicted Normal: {anomaly['predicted_normal']}")
        report.append(f"  Actual Contamination Rate: {anomaly['actual_contamination_rate']:.3f}")
        report.append(f"  Expected Contamination Rate: {model_info['contamination']}")
        report.append(f"  Anomaly Score Range: [{anomaly['anomaly_score_min']:.3f}, {anomaly['anomaly_score_max']:.3f}]")
        report.append(f"  Anomaly Score Mean: {anomaly['anomaly_score_mean']:.3f}")
        report.append(f"  Anomaly Score Std: {anomaly['anomaly_score_std']:.3f}")
        if anomaly.get('silhouette_score') is not None:
            report.append(f"  Silhouette Score: {anomaly['silhouette_score']:.3f}")
        report.append("")
        
        # Feature Analysis
        if 'feature_importance_scores' in evaluation['feature_analysis']:
            feature_analysis = evaluation['feature_analysis']
            report.append("FEATURE IMPORTANCE ANALYSIS:")
            report.append(f"  Most Important Feature: {feature_analysis['most_important_feature']}")
            report.append(f"  Least Important Feature: {feature_analysis['least_important_feature']}")
            report.append("  Feature Rankings:")
            for feature, importance in feature_analysis['feature_ranking']:
                report.append(f"    {feature}: {importance:.3f}")
            report.append("")
        
        # Supervised Metrics (if available)
        if 'supervised_metrics' in evaluation and 'error' not in evaluation['supervised_metrics']:
            supervised = evaluation['supervised_metrics']
            report.append("SUPERVISED LEARNING METRICS:")
            report.append(f"  Accuracy: {supervised['accuracy']:.3f}")
            report.append(f"  Precision: {supervised['precision']:.3f}")
            report.append(f"  Recall: {supervised['recall']:.3f}")
            report.append(f"  F1-Score: {supervised['f1_score']:.3f}")
            report.append(f"  Specificity: {supervised['specificity']:.3f}")
            report.append("")
            report.append("  Confusion Matrix:")
            cm = supervised['confusion_matrix']
            report.append(f"    True Negative: {cm['true_negative']}")
            report.append(f"    False Positive: {cm['false_positive']}")
            report.append(f"    False Negative: {cm['false_negative']}")
            report.append(f"    True Positive: {cm['true_positive']}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        return f"Error generating report: {str(e)}"