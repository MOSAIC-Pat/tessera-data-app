"""Simple Moving Average model."""

import pandas as pd
import numpy as np
from .base_model import BaseForecastModel


class SimpleMovingAverage(BaseForecastModel):
    """Simple Moving Average forecasting model."""

    def __init__(self):
        super().__init__('Simple Moving Average')
        self.window = 3
        self.data = None

    def fit(self, data: pd.DataFrame, window: int = 3, **kwargs) -> None:
        """
        Fit SMA model.

        Args:
            data: DataFrame with 'date' and 'value' columns
            window: Number of periods for moving average
        """
        self.window = window
        self.data = data.copy()
        self.parameters = {'window': window}

    def predict(self, periods: int) -> pd.DataFrame:
        """
        Generate forecast using SMA.

        Args:
            periods: Number of periods to forecast

        Returns:
            DataFrame with date, forecast, lower_bound, upper_bound
        """
        if self.data is None:
            raise ValueError("Model must be fit before predicting")

        # Calculate SMA for the last window periods
        last_values = self.data['value'].tail(self.window).values
        forecast_value = np.mean(last_values)

        # Generate future dates
        last_date = self.data['date'].max()
        freq = pd.infer_freq(self.data['date'])
        if not freq:
            freq = 'D'  # Default to daily

        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=periods,
            freq=freq
        )

        # Calculate standard deviation for confidence intervals
        std = self.data['value'].std()

        forecast_df = pd.DataFrame({
            'date': future_dates,
            'forecast': forecast_value,
            'lower_bound_80': forecast_value - 1.28 * std,
            'upper_bound_80': forecast_value + 1.28 * std,
            'lower_bound_95': forecast_value - 1.96 * std,
            'upper_bound_95': forecast_value + 1.96 * std
        })

        return forecast_df
