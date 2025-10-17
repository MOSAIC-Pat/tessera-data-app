"""Exponential Smoothing model."""

import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from .base_model import BaseForecastModel


class ExponentialSmoothing(BaseForecastModel):
    """Exponential Smoothing forecasting model."""

    def __init__(self):
        super().__init__('Exponential Smoothing')
        self.alpha = 0.3
        self.fitted_model = None
        self.data = None

    def fit(self, data: pd.DataFrame, alpha: float = 0.3, **kwargs) -> None:
        """
        Fit Exponential Smoothing model.

        Args:
            data: DataFrame with 'date' and 'value' columns
            alpha: Smoothing parameter (0-1)
        """
        self.alpha = alpha
        self.data = data.copy()

        # Fit the model
        self.fitted_model = SimpleExpSmoothing(data['value']).fit(
            smoothing_level=alpha,
            optimized=False
        )

        self.parameters = {'alpha': alpha}

    def predict(self, periods: int) -> pd.DataFrame:
        """
        Generate forecast using Exponential Smoothing.

        Args:
            periods: Number of periods to forecast

        Returns:
            DataFrame with date, forecast, lower_bound, upper_bound
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fit before predicting")

        # Generate forecast
        forecast_result = self.fitted_model.forecast(periods)

        # Generate future dates
        last_date = self.data['date'].max()
        freq = pd.infer_freq(self.data['date'])
        if not freq:
            freq = 'D'

        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=periods,
            freq=freq
        )

        # Calculate standard error for confidence intervals
        residuals = self.fitted_model.resid
        std_error = np.std(residuals)

        forecast_df = pd.DataFrame({
            'date': future_dates,
            'forecast': forecast_result.values,
            'lower_bound_80': forecast_result.values - 1.28 * std_error,
            'upper_bound_80': forecast_result.values + 1.28 * std_error,
            'lower_bound_95': forecast_result.values - 1.96 * std_error,
            'upper_bound_95': forecast_result.values + 1.96 * std_error
        })

        return forecast_df
