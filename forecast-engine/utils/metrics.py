"""Forecast accuracy metrics calculation."""

import numpy as np
import pandas as pd
from typing import Dict


def calculate_metrics(actual: pd.Series, forecast: pd.Series) -> Dict[str, float]:
    """
    Calculate forecast accuracy metrics.

    Args:
        actual: Series of actual values
        forecast: Series of forecasted values

    Returns:
        Dictionary with accuracy metrics
    """
    # Remove NaN values
    mask = ~(actual.isna() | forecast.isna())
    actual = actual[mask]
    forecast = forecast[mask]

    if len(actual) == 0:
        return {
            'mape': None,
            'mad': None,
            'rmse': None,
            'bias': None,
            'tracking_signal': None
        }

    # Mean Absolute Percentage Error
    mape = np.mean(np.abs((actual - forecast) / actual)) * 100

    # Mean Absolute Deviation
    mad = np.mean(np.abs(actual - forecast))

    # Root Mean Square Error
    rmse = np.sqrt(np.mean((actual - forecast) ** 2))

    # Bias
    bias = np.mean(forecast - actual)

    # Tracking Signal
    cumulative_error = np.sum(forecast - actual)
    tracking_signal = cumulative_error / mad if mad != 0 else 0

    return {
        'mape': round(float(mape), 4),
        'mad': round(float(mad), 2),
        'rmse': round(float(rmse), 2),
        'bias': round(float(bias), 4),
        'tracking_signal': round(float(tracking_signal), 4)
    }
