"""ARIMA model."""

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from .base_model import BaseForecastModel


class ARIMAModel(BaseForecastModel):
    """ARIMA (AutoRegressive Integrated Moving Average) model."""

    def __init__(self):
        super().__init__('ARIMA')
        self.fitted_model = None
        self.data = None

    def fit(
        self,
        data: pd.DataFrame,
        order: tuple = (1, 1, 1),
        **kwargs
    ) -> None:
        """
        Fit ARIMA model.

        Args:
            data: DataFrame with 'date' and 'value' columns
            order: Tuple (p, d, q) for ARIMA parameters
                   p: autoregressive order
                   d: differencing order
                   q: moving average order
        """
        self.data = data.copy()

        # Fit the model
        self.fitted_model = ARIMA(
            data['value'],
            order=order
        ).fit()

        self.parameters = {
            'p': order[0],
            'd': order[1],
            'q': order[2]
        }

    def predict(self, periods: int) -> pd.DataFrame:
        """
        Generate forecast using ARIMA.

        Args:
            periods: Number of periods to forecast

        Returns:
            DataFrame with date, forecast, lower_bound, upper_bound
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fit before predicting")

        # Generate forecast with confidence intervals
        forecast_obj = self.fitted_model.get_forecast(steps=periods)
        forecast_result = forecast_obj.predicted_mean
        forecast_ci_95 = forecast_obj.conf_int()

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

        # Calculate 80% confidence intervals
        residuals = self.fitted_model.resid
        std_error = np.std(residuals)

        forecast_df = pd.DataFrame({
            'date': future_dates,
            'forecast': forecast_result.values,
            'lower_bound_80': forecast_result.values - 1.28 * std_error,
            'upper_bound_80': forecast_result.values + 1.28 * std_error,
            'lower_bound_95': forecast_ci_95.iloc[:, 0].values,
            'upper_bound_95': forecast_ci_95.iloc[:, 1].values
        })

        return forecast_df
