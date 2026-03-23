"""
Feature Engineering Module for TRINETRA AI Trade Fraud Detection System

This module contains functions to generate fraud detection features from raw transaction data.
Each feature is designed to capture specific patterns that may indicate fraudulent trade activity.
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_price_anomaly_score(df: pd.DataFrame) -> pd.Series:
    """
    Calculate price anomaly score from price deviation.
    
    Formula: price_anomaly_score = abs(price_deviation)
    
    This feature measures the absolute deviation from market price, where higher values
    indicate greater price anomalies that could suggest fraudulent pricing.
    
    Args:
        df (pd.DataFrame): DataFrame containing transaction data with 'price_deviation' column
        
    Returns:
        pd.Series: Series containing price anomaly scores
        
    Raises:
        KeyError: If 'price_deviation' column is missing from DataFrame
        ValueError: If DataFrame is empty or contains invalid data
    """
    logger.info("Calculating price anomaly scores...")
    
    # Validate input DataFrame
    if df is None or df.empty:
        raise ValueError("Input DataFrame cannot be None or empty")
    
    # Check if required column exists
    if 'price_deviation' not in df.columns:
        raise KeyError("Column 'price_deviation' not found in DataFrame")
    
    try:
        # Calculate absolute value of price deviation
        price_anomaly_score = df['price_deviation'].abs()
        
        # Handle any NaN values by filling with 0 (no anomaly)
        price_anomaly_score = price_anomaly_score.fillna(0.0)
        
        # Log statistics
        logger.info(f"Price anomaly score statistics:")
        logger.info(f"  Mean: {price_anomaly_score.mean():.4f}")
        logger.info(f"  Std: {price_anomaly_score.std():.4f}")
        logger.info(f"  Min: {price_anomaly_score.min():.4f}")
        logger.info(f"  Max: {price_anomaly_score.max():.4f}")
        logger.info(f"  Non-null values: {price_anomaly_score.count()}/{len(price_anomaly_score)}")
        
        return price_anomaly_score
        
    except Exception as e:
        logger.error(f"Error calculating price anomaly score: {str(e)}")
        raise


def calculate_route_risk_score(df: pd.DataFrame) -> pd.Series:
    """
    Calculate route risk score from route anomaly indicator.
    
    Formula: route_risk_score = route_anomaly
    
    Args:
        df (pd.DataFrame): DataFrame containing transaction data with 'route_anomaly' column
        
    Returns:
        pd.Series: Series containing route risk scores
    """
    logger.info("Calculating route risk scores...")
    
    if df is None or df.empty:
        raise ValueError("Input DataFrame cannot be None or empty")
    
    if 'route_anomaly' not in df.columns:
        raise KeyError("Column 'route_anomaly' not found in DataFrame")
    
    try:
        route_risk_score = df['route_anomaly'].fillna(0.0)
        logger.info(f"Route risk score - Unique values: {route_risk_score.unique()}")
        return route_risk_score
    except Exception as e:
        logger.error(f"Error calculating route risk score: {str(e)}")
        raise


def calculate_company_network_risk(df: pd.DataFrame) -> pd.Series:
    """
    Calculate company network risk from company risk score.
    
    Formula: company_network_risk = company_risk_score
    
    Args:
        df (pd.DataFrame): DataFrame containing transaction data with 'company_risk_score' column
        
    Returns:
        pd.Series: Series containing company network risk scores
    """
    logger.info("Calculating company network risk scores...")
    
    if df is None or df.empty:
        raise ValueError("Input DataFrame cannot be None or empty")
    
    if 'company_risk_score' not in df.columns:
        raise KeyError("Column 'company_risk_score' not found in DataFrame")
    
    try:
        company_network_risk = df['company_risk_score'].fillna(0.0)
        logger.info(f"Company network risk - Mean: {company_network_risk.mean():.4f}")
        return company_network_risk
    except Exception as e:
        logger.error(f"Error calculating company network risk: {str(e)}")
        raise


def calculate_port_congestion_score(df: pd.DataFrame) -> pd.Series:
    """
    Calculate port congestion score from port activity index.
    
    Formula: port_congestion_score = port_activity_index
    
    Args:
        df (pd.DataFrame): DataFrame containing transaction data with 'port_activity_index' column
        
    Returns:
        pd.Series: Series containing port congestion scores
    """
    logger.info("Calculating port congestion scores...")
    
    if df is None or df.empty:
        raise ValueError("Input DataFrame cannot be None or empty")
    
    if 'port_activity_index' not in df.columns:
        raise KeyError("Column 'port_activity_index' not found in DataFrame")
    
    try:
        port_congestion_score = df['port_activity_index'].fillna(1.0)  # Default to normal activity
        logger.info(f"Port congestion score - Mean: {port_congestion_score.mean():.4f}")
        return port_congestion_score
    except Exception as e:
        logger.error(f"Error calculating port congestion score: {str(e)}")
        raise


def calculate_shipment_duration_risk(df: pd.DataFrame) -> pd.Series:
    """
    Calculate shipment duration risk normalized by distance.
    
    Formula: shipment_duration_risk = shipment_duration_days / distance_km
    
    Args:
        df (pd.DataFrame): DataFrame containing transaction data with required columns
        
    Returns:
        pd.Series: Series containing shipment duration risk scores
    """
    logger.info("Calculating shipment duration risk scores...")
    
    if df is None or df.empty:
        raise ValueError("Input DataFrame cannot be None or empty")
    
    required_columns = ['shipment_duration_days', 'distance_km']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")
    
    try:
        # Handle division by zero by replacing zero distances with a small value
        distance_safe = df['distance_km'].replace(0, 1)  # Avoid division by zero
        
        shipment_duration_risk = df['shipment_duration_days'] / distance_safe
        shipment_duration_risk = shipment_duration_risk.fillna(0.0)
        
        logger.info(f"Shipment duration risk - Mean: {shipment_duration_risk.mean():.6f}")
        return shipment_duration_risk
    except Exception as e:
        logger.error(f"Error calculating shipment duration risk: {str(e)}")
        raise


def calculate_volume_spike_score(df: pd.DataFrame) -> pd.Series:
    """
    Calculate volume spike score from cargo volume and quantity.
    
    Formula: volume_spike_score = cargo_volume / quantity
    
    Args:
        df (pd.DataFrame): DataFrame containing transaction data with required columns
        
    Returns:
        pd.Series: Series containing volume spike scores
    """
    logger.info("Calculating volume spike scores...")
    
    if df is None or df.empty:
        raise ValueError("Input DataFrame cannot be None or empty")
    
    required_columns = ['cargo_volume', 'quantity']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")
    
    try:
        # Handle division by zero by replacing zero quantities with a small value
        quantity_safe = df['quantity'].replace(0, 1)  # Avoid division by zero
        
        volume_spike_score = df['cargo_volume'] / quantity_safe
        volume_spike_score = volume_spike_score.fillna(0.0)
        
        logger.info(f"Volume spike score - Mean: {volume_spike_score.mean():.4f}")
        return volume_spike_score
    except Exception as e:
        logger.error(f"Error calculating volume spike score: {str(e)}")
        raise


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate all fraud detection features from raw transaction data.
    
    This function orchestrates the calculation of all six fraud detection features:
    1. price_anomaly_score - Absolute price deviation from market
    2. route_risk_score - Route anomaly indicator
    3. company_network_risk - Company risk assessment
    4. port_congestion_score - Port activity level
    5. shipment_duration_risk - Duration normalized by distance
    6. volume_spike_score - Volume per unit quantity
    
    Args:
        df (pd.DataFrame): Raw transaction DataFrame
        
    Returns:
        pd.DataFrame: DataFrame enriched with all fraud detection features
        
    Raises:
        ValueError: If input DataFrame is invalid
        KeyError: If required columns are missing
    """
    logger.info("Starting feature engineering pipeline...")
    
    if df is None or df.empty:
        raise ValueError("Input DataFrame cannot be None or empty")
    
    # Create a copy to avoid modifying the original DataFrame
    enriched_df = df.copy()
    
    try:
        # Calculate all features
        enriched_df['price_anomaly_score'] = calculate_price_anomaly_score(df)
        enriched_df['route_risk_score'] = calculate_route_risk_score(df)
        enriched_df['company_network_risk'] = calculate_company_network_risk(df)
        enriched_df['port_congestion_score'] = calculate_port_congestion_score(df)
        enriched_df['shipment_duration_risk'] = calculate_shipment_duration_risk(df)
        enriched_df['volume_spike_score'] = calculate_volume_spike_score(df)
        
        logger.info("Feature engineering completed successfully")
        logger.info(f"Original columns: {len(df.columns)}")
        logger.info(f"Enriched columns: {len(enriched_df.columns)}")
        logger.info(f"New features added: {len(enriched_df.columns) - len(df.columns)}")
        
        return enriched_df
        
    except Exception as e:
        logger.error(f"Error in feature engineering pipeline: {str(e)}")
        raise


if __name__ == "__main__":
    """
    Test the feature engineering functions with sample data.
    """
    # This section can be used for testing during development
    print("Feature Engineering Module - TRINETRA AI")
    print("Run tests using: python -m pytest backend/test_feature_engineering.py")