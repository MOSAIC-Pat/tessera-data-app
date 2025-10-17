"""Database connection utility for forecast engine."""

import os
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


class DatabaseConnection:
    """Manages database connections for forecast operations."""

    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.schema_name = os.getenv('SCHEMA_NAME', 'raw_tenant_data')
        self.engine = None

    def connect(self):
        """Create database engine connection."""
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")

        self.engine = create_engine(self.database_url)
        return self.engine

    def get_historical_sales(
        self,
        tenant_id: str,
        product_id: Optional[str] = None,
        location_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch historical sales data for forecasting.

        Args:
            tenant_id: Tenant UUID
            product_id: Optional product UUID filter
            location_id: Optional location UUID filter
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)

        Returns:
            DataFrame with sales data
        """
        if not self.engine:
            self.connect()

        query = f"""
        SELECT
            sale_date,
            product_external_id,
            location_external_id,
            SUM(quantity) as quantity,
            SUM(total_amount) as revenue
        FROM {self.schema_name}.tenant_sales
        WHERE tenant_id = :tenant_id
        """

        params = {'tenant_id': tenant_id}

        if product_id:
            query += " AND product_external_id = :product_id"
            params['product_id'] = product_id

        if location_id:
            query += " AND location_external_id = :location_id"
            params['location_id'] = location_id

        if start_date:
            query += " AND sale_date >= :start_date"
            params['start_date'] = start_date

        if end_date:
            query += " AND sale_date <= :end_date"
            params['end_date'] = end_date

        query += """
        GROUP BY sale_date, product_external_id, location_external_id
        ORDER BY sale_date
        """

        df = pd.read_sql(text(query), self.engine, params=params)
        df['sale_date'] = pd.to_datetime(df['sale_date'])

        # Rename columns to standardize
        df = df.rename(columns={
            'product_external_id': 'product_id',
            'location_external_id': 'location_id'
        })

        return df

    def save_forecast(
        self,
        forecast_id: str,
        forecast_data: pd.DataFrame
    ):
        """
        Save forecast data to database.

        Args:
            forecast_id: UUID of the forecast header
            forecast_data: DataFrame with forecast results
        """
        if not self.engine:
            self.connect()

        forecast_data.to_sql(
            'forecast_data',
            self.engine,
            schema=self.schema_name,
            if_exists='append',
            index=False
        )

    def create_forecast_header(
        self,
        tenant_id: str,
        forecast_name: str,
        model_type: str,
        time_granularity: str,
        forecast_horizon_days: int,
        model_parameters: dict,
        metrics: dict,
        created_by: str
    ) -> str:
        """
        Create forecast header record.

        Args:
            tenant_id: Tenant UUID
            forecast_name: Name of forecast
            model_type: Type of model used
            time_granularity: daily, weekly, monthly, quarterly
            forecast_horizon_days: Number of days to forecast
            model_parameters: Model configuration dict
            metrics: Accuracy metrics dict (mape, mad, rmse, bias, tracking_signal)
            created_by: User UUID

        Returns:
            forecast_id UUID
        """
        if not self.engine:
            self.connect()

        import json

        query = text(f"""
        INSERT INTO {self.schema_name}.forecasts (
            tenant_id, forecast_name, model_type, time_granularity,
            forecast_horizon_days, model_parameters, mape, mad, rmse,
            bias, tracking_signal, created_by
        ) VALUES (
            :tenant_id, :forecast_name, :model_type, :time_granularity,
            :forecast_horizon_days, :model_parameters, :mape, :mad, :rmse,
            :bias, :tracking_signal, :created_by
        ) RETURNING id
        """)

        with self.engine.connect() as conn:
            result = conn.execute(query, {
                'tenant_id': tenant_id,
                'forecast_name': forecast_name,
                'model_type': model_type,
                'time_granularity': time_granularity,
                'forecast_horizon_days': forecast_horizon_days,
                'model_parameters': json.dumps(model_parameters),
                'mape': metrics.get('mape'),
                'mad': metrics.get('mad'),
                'rmse': metrics.get('rmse'),
                'bias': metrics.get('bias'),
                'tracking_signal': metrics.get('tracking_signal'),
                'created_by': created_by
            })
            conn.commit()
            forecast_id = result.fetchone()[0]

        return str(forecast_id)

    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
