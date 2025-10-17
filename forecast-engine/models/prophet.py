"""Prophet model."""

import pandas as pd
from prophet import Prophet
from .base_model import BaseForecastModel


class ProphetModel(BaseForecastModel):
    """Facebook Prophet forecasting model."""

    def __init__(self):
        super().__init__('Prophet')
        self.fitted_model = None
        self.data = None

    def fit(
        self,
        data: pd.DataFrame,
        yearly_seasonality: bool = True,
        weekly_seasonality: bool = True,
        daily_seasonality: bool = False,
        **kwargs
    ) -> None:
        """
        Fit Prophet model.

        Args:
            data: DataFrame with 'date' and 'value' columns
            yearly_seasonality: Enable yearly seasonality
            weekly_seasonality: Enable weekly seasonality
            daily_seasonality: Enable daily seasonality
        """
        self.data = data.copy()

        # Prophet requires 'ds' and 'y' column names
        prophet_data = pd.DataFrame({
            'ds': data['date'],
            'y': data['value']
        })

        # Initialize and fit model
        self.fitted_model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality
        )
        self.fitted_model.fit(prophet_data)

        self.parameters = {
            'yearly_seasonality': yearly_seasonality,
            'weekly_seasonality': weekly_seasonality,
            'daily_seasonality': daily_seasonality
        }

    def predict(self, periods: int) -> pd.DataFrame:
        """
        Generate forecast using Prophet.

        Args:
            periods: Number of periods to forecast

        Returns:
            DataFrame with date, forecast, lower_bound, upper_bound
        """
        if self.fitted_model is None:
            raise ValueError("Model must be fit before predicting")

        # Create future dataframe
        freq = pd.infer_freq(self.data['date'])
        if not freq:
            freq = 'D'

        future = self.fitted_model.make_future_dataframe(
            periods=periods,
            freq=freq
        )

        # Generate forecast
        forecast_result = self.fitted_model.predict(future)

        # Get only future predictions
        forecast_result = forecast_result.tail(periods)

        # Prophet provides yhat (forecast), yhat_lower, yhat_upper
        # Convert 95% CI to 80% CI approximately
        forecast_df = pd.DataFrame({
            'date': forecast_result['ds'].values,
            'forecast': forecast_result['yhat'].values,
            'lower_bound_80': forecast_result['yhat_lower'].values * 0.65 + forecast_result['yhat'].values * 0.35,
            'upper_bound_80': forecast_result['yhat_upper'].values * 0.65 + forecast_result['yhat'].values * 0.35,
            'lower_bound_95': forecast_result['yhat_lower'].values,
            'upper_bound_95': forecast_result['yhat_upper'].values
        })

        return forecast_df
