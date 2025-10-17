"""Main script to run forecasting models at product/location level."""

import sys
import argparse
import pandas as pd
from datetime import datetime
from sqlalchemy import text

from utils.db_connection import DatabaseConnection
from models import (
    SimpleMovingAverage,
    WeightedMovingAverage,
    ExponentialSmoothing,
    HoltWinters,
    ARIMAModel,
    ProphetModel
)


def run_forecast(
    tenant_id: str,
    model_type: str,
    product_id: str = None,
    location_id: str = None,
    forecast_horizon_days: int = 90,
    time_granularity: str = 'daily',
    created_by: str = None
):
    """
    Run forecasting model at product/location level and save results to database.

    Args:
        tenant_id: Tenant UUID
        model_type: One of 'sma', 'wma', 'exp-smoothing', 'holt-winters', 'arima', 'prophet'
        product_id: Optional product ID (if not provided, forecasts all products)
        location_id: Optional location ID (if not provided, forecasts all locations)
        forecast_horizon_days: Number of days to forecast
        time_granularity: daily, weekly, monthly, quarterly
        created_by: User UUID
    """
    print(f"\n🚀 Starting forecast run...")
    print(f"Model: {model_type}")
    print(f"Tenant: {tenant_id}")
    print(f"Horizon: {forecast_horizon_days} days")
    print(f"Granularity: {time_granularity}")

    # Initialize database connection
    db = DatabaseConnection()

    # Fetch historical data
    print("\n📊 Fetching historical sales data...")
    historical_data = db.get_historical_sales(
        tenant_id=tenant_id,
        product_id=product_id,
        location_id=location_id
    )

    if len(historical_data) == 0:
        print("❌ No historical data found!")
        return

    print(f"✓ Found {len(historical_data)} historical records")

    # Get unique product/location combinations
    if product_id and location_id:
        combinations = [(product_id, location_id)]
    else:
        combinations = historical_data[['product_id', 'location_id']].drop_duplicates().values.tolist()
        combinations = [tuple(c) for c in combinations]

    print(f"\n🎯 Will generate {len(combinations)} product/location forecasts\n")

    all_forecast_data = []
    successful_forecasts = 0

    for prod_id, loc_id in combinations:
        print(f"--- Product: {prod_id}, Location: {loc_id} ---")

        # Filter data for this product/location
        filtered = historical_data[
            (historical_data['product_id'] == prod_id) &
            (historical_data['location_id'] == loc_id)
        ].copy()

        if len(filtered) < 10:
            print(f"  ⚠️  Skipping: Only {len(filtered)} records (need at least 10)\n")
            continue

        # Aggregate by time granularity
        if time_granularity == 'weekly':
            filtered['date'] = pd.to_datetime(filtered['sale_date']).dt.to_period('W').dt.start_time
        elif time_granularity == 'monthly':
            filtered['date'] = pd.to_datetime(filtered['sale_date']).dt.to_period('M').dt.start_time
        elif time_granularity == 'quarterly':
            filtered['date'] = pd.to_datetime(filtered['sale_date']).dt.to_period('Q').dt.start_time
        else:
            filtered['date'] = pd.to_datetime(filtered['sale_date'])

        aggregated = filtered.groupby('date').agg({
            'quantity': 'sum',
            'revenue': 'sum'
        }).reset_index()

        aggregated = aggregated.rename(columns={'quantity': 'value'})
        aggregated = aggregated[['date', 'value']].sort_values('date')

        print(f"  ✓ {len(aggregated)} {time_granularity} periods")

        # Initialize model
        model_map = {
            'sma': SimpleMovingAverage(),
            'wma': WeightedMovingAverage(),
            'exp-smoothing': ExponentialSmoothing(),
            'holt-winters': HoltWinters(),
            'arima': ARIMAModel(),
            'prophet': ProphetModel()
        }

        if model_type not in model_map:
            print(f"  ❌ Unknown model type: {model_type}\n")
            continue

        model = model_map[model_type]

        # Fit model
        try:
            if model_type == 'holt-winters':
                seasonal_periods = min(12 if time_granularity == 'monthly' else 7, len(aggregated) // 2)
                model.fit(aggregated, seasonal_periods=seasonal_periods)
            else:
                model.fit(aggregated)
            print(f"  ✓ Model fitted")
        except Exception as e:
            print(f"  ❌ Error fitting: {e}\n")
            continue

        # Calculate periods
        if time_granularity == 'weekly':
            periods = forecast_horizon_days // 7
        elif time_granularity == 'monthly':
            periods = forecast_horizon_days // 30
        elif time_granularity == 'quarterly':
            periods = forecast_horizon_days // 90
        else:
            periods = forecast_horizon_days

        # Generate forecast
        try:
            forecast_df = model.predict(periods)
            forecast_df['product_id'] = prod_id
            forecast_df['location_id'] = loc_id
            all_forecast_data.append(forecast_df)
            successful_forecasts += 1
            print(f"  ✓ Forecast generated ({periods} periods)\n")
        except Exception as e:
            print(f"  ❌ Error forecasting: {e}\n")
            continue

    if successful_forecasts == 0:
        print("❌ No forecasts were generated!")
        db.close()
        return

    print(f"✅ Generated {successful_forecasts} forecasts successfully")

    # Combine all forecast data
    combined_forecast_df = pd.concat(all_forecast_data, ignore_index=True)

    # Calculate aggregate metrics (using first combination as sample)
    print("\n📊 Calculating metrics...")
    sample_model = model_map[model_type]
    if len(aggregated) > 30:
        test_size = min(30, len(aggregated) // 4)
        metrics = sample_model.validate(aggregated, test_size=test_size)
    else:
        metrics = {'mape': None, 'mad': None, 'rmse': None, 'bias': None, 'tracking_signal': None}

    print(f"  Sample MAPE: {metrics['mape']:.2f}%" if metrics['mape'] else "  No validation metrics")

    # Save to database
    print("\n💾 Saving to database...")

    forecast_name = f"{model_map[model_type].name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    # Get valid user_id
    if not created_by:
        user_query = f"SELECT id FROM {db.schema_name}.users WHERE tenant_id = :tenant_id LIMIT 1"
        with db.engine.connect() as conn:
            result = conn.execute(text(user_query), {'tenant_id': tenant_id})
            user_row = result.fetchone()
            created_by = str(user_row[0]) if user_row else None

    forecast_id = db.create_forecast_header(
        tenant_id=tenant_id,
        forecast_name=forecast_name,
        model_type=model_type,
        time_granularity=time_granularity,
        forecast_horizon_days=forecast_horizon_days,
        model_parameters=sample_model.parameters,
        metrics=metrics,
        created_by=created_by
    )

    print(f"✓ Forecast header: {forecast_id}")

    # Prepare data for insertion
    forecast_data = combined_forecast_df.copy()
    forecast_data['forecast_id'] = forecast_id
    forecast_data['customer_id'] = None
    forecast_data['forecast_date'] = forecast_data['date']
    forecast_data['period_start'] = forecast_data['date']
    forecast_data['period_end'] = forecast_data['date']
    forecast_data['forecasted_quantity'] = forecast_data['forecast']
    forecast_data['forecasted_value'] = None

    forecast_data = forecast_data[[
        'forecast_id', 'product_id', 'location_id', 'customer_id',
        'forecast_date', 'period_start', 'period_end',
        'forecasted_quantity', 'forecasted_value',
        'lower_bound_80', 'upper_bound_80',
        'lower_bound_95', 'upper_bound_95'
    ]]

    db.save_forecast(forecast_id, forecast_data)
    print(f"✓ Saved {len(forecast_data)} forecast records")

    db.close()

    print(f"\n✅ Forecast completed!")
    print(f"Forecast ID: {forecast_id}")
    print(f"Total forecasts: {successful_forecasts} product/location combinations")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run forecasting models')
    parser.add_argument('--tenant-id', required=True, help='Tenant UUID')
    parser.add_argument('--model', required=True, choices=['sma', 'wma', 'exp-smoothing', 'holt-winters', 'arima', 'prophet'])
    parser.add_argument('--product-id', help='Product ID (optional - forecasts all if not specified)')
    parser.add_argument('--location-id', help='Location ID (optional - forecasts all if not specified)')
    parser.add_argument('--horizon', type=int, default=90, help='Forecast horizon in days')
    parser.add_argument('--granularity', choices=['daily', 'weekly', 'monthly', 'quarterly'], default='daily')
    parser.add_argument('--user-id', help='User UUID who created forecast')

    args = parser.parse_args()

    run_forecast(
        tenant_id=args.tenant_id,
        model_type=args.model,
        product_id=args.product_id,
        location_id=args.location_id,
        forecast_horizon_days=args.horizon,
        time_granularity=args.granularity,
        created_by=args.user_id
    )
