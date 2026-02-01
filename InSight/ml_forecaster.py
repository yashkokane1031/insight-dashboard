"""
ML Forecaster Module for Predictive Analytics

This module provides lightweight time-series forecasting using scikit-learn.
It analyzes historical data and generates predictions for anomaly detection.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import logging

logger = logging.getLogger(__name__)


class Forecaster:
    """
    Lightweight forecaster using Polynomial Regression.
    
    Uses the last N hours of data to predict the next hour's values.
    Also calculates confidence intervals for anomaly detection.
    """
    
    def __init__(self, lookback_hours: int = 24, forecast_points: int = 12):
        """
        Initialize the forecaster.
        
        Args:
            lookback_hours: Hours of historical data to use for training
            forecast_points: Number of future points to predict (at 5-min intervals = 1 hour)
        """
        self.lookback_hours = lookback_hours
        self.forecast_points = forecast_points
        self.model = None
        self.poly_features = PolynomialFeatures(degree=2)
    
    def prepare_data(self, data_points: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for training.
        
        Args:
            data_points: List of dicts with 'timestamp' and 'value' keys
        
        Returns:
            Tuple of (X, y) arrays where X is minutes since start, y is values
        """
        if not data_points:
            raise ValueError("No data points provided")
        
        # Parse timestamps and extract values
        timestamps = []
        values = []
        
        for dp in data_points:
            ts = dp.get('timestamp')
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            timestamps.append(ts)
            values.append(dp.get('value', 0))
        
        # Convert to minutes since first point
        start_time = min(timestamps)
        X = np.array([(ts - start_time).total_seconds() / 60 for ts in timestamps]).reshape(-1, 1)
        y = np.array(values)
        
        return X, y, start_time, timestamps[-1]
    
    def fit(self, data_points: List[Dict]) -> 'Forecaster':
        """
        Fit the model on historical data.
        
        Args:
            data_points: List of dicts with 'timestamp' and 'value' keys
        
        Returns:
            self for chaining
        """
        X, y, self.start_time, self.last_time = self.prepare_data(data_points)
        
        # Transform features to polynomial
        X_poly = self.poly_features.fit_transform(X)
        
        # Fit the model
        self.model = LinearRegression()
        self.model.fit(X_poly, y)
        
        # Calculate residuals for confidence interval
        predictions = self.model.predict(X_poly)
        self.residual_std = np.std(y - predictions)
        
        # Store the last X value for forecasting
        self.last_x = X[-1, 0]
        
        logger.info(f"Model trained on {len(data_points)} points, residual std: {self.residual_std:.2f}")
        
        return self
    
    def predict(self) -> Dict:
        """
        Generate forecast for the next hour.
        
        Returns:
            Dict with 'predicted' list and 'anomaly_threshold' values
        """
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")
        
        # Generate future time points (5-minute intervals)
        future_x = np.array([
            self.last_x + (i + 1) * 5  # 5-minute intervals
            for i in range(self.forecast_points)
        ]).reshape(-1, 1)
        
        # Generate timestamps for predictions
        future_timestamps = [
            self.last_time + timedelta(minutes=(i + 1) * 5)
            for i in range(self.forecast_points)
        ]
        
        # Transform and predict
        future_x_poly = self.poly_features.transform(future_x)
        predictions = self.model.predict(future_x_poly)
        
        # Calculate confidence intervals (2 standard deviations)
        confidence_interval = 2 * self.residual_std
        
        return {
            "predicted": [
                {
                    "timestamp": ts.isoformat(),
                    "value": float(pred),
                    "lower_bound": float(pred - confidence_interval),
                    "upper_bound": float(pred + confidence_interval)
                }
                for ts, pred in zip(future_timestamps, predictions)
            ],
            "confidence_interval": float(confidence_interval),
            "model_info": {
                "type": "polynomial_regression",
                "degree": 2,
                "lookback_hours": self.lookback_hours,
                "training_points": int(self.last_x / 5) + 1
            }
        }
    
    def detect_anomalies(self, data_points: List[Dict]) -> List[Dict]:
        """
        Detect anomalies in the given data points.
        
        An anomaly is a point that falls outside 2.5 standard deviations
        from the predicted value.
        
        Args:
            data_points: List of dicts with 'timestamp' and 'value' keys
        
        Returns:
            List of anomaly points with original data + 'is_anomaly' flag + 'deviation'
        """
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")
        
        X, y, _, _ = self.prepare_data(data_points)
        X_poly = self.poly_features.transform(X)
        predictions = self.model.predict(X_poly)
        
        threshold = 2.5 * self.residual_std
        anomalies = []
        
        for i, (dp, actual, predicted) in enumerate(zip(data_points, y, predictions)):
            deviation = abs(actual - predicted)
            is_anomaly = deviation > threshold
            
            result = {
                **dp,
                "predicted_value": float(predicted),
                "deviation": float(deviation),
                "is_anomaly": is_anomaly
            }
            
            if is_anomaly:
                anomalies.append(result)
        
        return anomalies


def create_forecast(data_points: List[Dict], lookback_hours: int = 24) -> Dict:
    """
    Convenience function to generate a forecast from data points.
    
    Args:
        data_points: List of dicts with 'timestamp' and 'value' keys
        lookback_hours: Hours of data to use for training
    
    Returns:
        Forecast result dict
    """
    if len(data_points) < 10:
        return {
            "error": "Insufficient data",
            "message": f"Need at least 10 data points, got {len(data_points)}"
        }
    
    forecaster = Forecaster(lookback_hours=lookback_hours)
    forecaster.fit(data_points)
    
    forecast = forecaster.predict()
    anomalies = forecaster.detect_anomalies(data_points)
    
    return {
        **forecast,
        "anomalies": anomalies,
        "anomaly_count": len(anomalies)
    }
