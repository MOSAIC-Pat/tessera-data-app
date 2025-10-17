"""Holt-Winters Exponential Smoothing model."""

import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing as HW
from .base_model import BaseForecastModel


class HoltWinters(BaseForecastModel):
    """Holt-Winters Exponential Smoothing model with trend and seasonality."""

    def __init__(self):
        super().__init__('Holt-Winters')
        self.fitted_model = None
        self.data = None

    def fit(
        self,
        data: pd.DataFrame,
        seasonal_periods: int = 12,
        trend: str = 'add',
        seasonal: str = 'add',
        **kwargs
    ) -> None:
        """
        Fit Holt-Winters model.

        Args:
            data: DataFrame with 'date' and 'value' columns
            seasonal_periods: Number of periods in a season
            trend: 'add' or 'mul' for additive/multiplicative trend
            seasonal: 'add' or 'mul' for additive/multiplicative seasonality
        """
        self.data = data.copy()

        # Fit the model
        self.fitted_model = HW(
            data['value'],
            seasonal_periods=seasonal_periods,
            trend=trend,
            seasonal=seasonal
        ).fit()

        self.parameters = {
            'seasonal_periods': seasonal_periods,
            'trend': trend,
            'seasonal': seasonal
        }

    def predict(self, periods: int) -> pd.DataFrame:
        """
        Generate forecast using Holt-Winters.

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

        # Calculate confidence intervals using residuals
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
