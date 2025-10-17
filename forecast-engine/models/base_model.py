"""Base class for all forecasting models."""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Tuple


class BaseForecastModel(ABC):
    """Abstract base class for forecast models."""

    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.parameters = {}

    @abstractmethod
    def fit(self, data: pd.DataFrame, **kwargs) -> None:
        """
        Fit the model to historical data.

        Args:
            data: DataFrame with 'date' and 'value' columns
            **kwargs: Model-specific parameters
        """
        pass

    @abstractmethod
    def predict(self, periods: int) -> pd.DataFrame:
        """
        Generate forecast for specified periods.

        Args:
            periods: Number of periods to forecast

        Returns:
            DataFrame with forecasted values and confidence intervals
        """
        pass

    def validate(self, data: pd.DataFrame, test_size: int = 30) -> Dict[str, float]:
        """
        Validate model on holdout data.

        Args:
            data: Full dataset
            test_size: Number of periods to hold out

        Returns:
            Dictionary with accuracy metrics
        """
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils.metrics import calculate_metrics

        train = data[:-test_size]
        test = data[-test_size:]

        self.fit(train)
        forecast_df = self.predict(test_size)

        metrics = calculate_metrics(
            actual=test['value'],
            forecast=forecast_df['forecast']
        )

        return metrics
