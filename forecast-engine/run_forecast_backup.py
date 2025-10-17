"""Main script to run forecasting models."""

import sys
import argparse
import pandas as pd
from datetime import datetime, timedelta
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
    customer_id: str = None,
    forecast_horizon_days: int = 90,
    time_granularity: str = 'daily',
    forecast_level: str = 'product_location',  # 'product_location' or 'product_location_customer'
    created_by: str = None
):
    """
    Run forecasting model and save results to database.

    Args:
        tenant_id: Tenant UUID
        model_type: One of 'sma', 'wma', 'exp-smoothing', 'holt-winters', 'arima', 'prophet'
        product_id: Optional product UUID (if not provided, forecasts all products)
        location_id: Optional location UUID (if not provided, forecasts all locations)
        customer_id: Optional customer UUID (if not provided, aggregates customers)
        forecast_horizon_days: Number of days to forecast
        time_granularity: daily, weekly, monthly, quarterly
        forecast_level: 'product_location' or 'product_location_customer'
        created_by: User UUID
    """
    print(f"\n🚀 Starting forecast run...")
    print(f"Model: {model_type}")
    print(f"Tenant: {tenant_id}")
    print(f"Horizon: {forecast_horizon_days} days")

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

    # Determine forecast dimensions
    if forecast_level == 'product_location_customer':
        group_cols = ['product_id', 'location_id', 'customer_id'] if 'customer_id' in historical_data.columns else ['product_id', 'location_id']
    else:
        group_cols = ['product_id', 'location_id']

    # Get unique combinations to forecast
    if product_id and location_id:
        # Single forecast for specified product/location
        combinations = [(product_id, location_id)]
    else:
        # Get all unique combinations
        combinations = historical_data[group_cols].drop_duplicates().values.tolist()
        combinations = [tuple(c) for c in combinations]

    print(f"\n🎯 Will generate {len(combinations)} separate forecasts")
    print(f"   Forecast level: {forecast_level}")

    all_forecast_data = []
    forecast_count = 0

    for combo in combinations:
        if len(combo) == 2:
            prod_id, loc_id = combo
            cust_id = None
        else:
            prod_id, loc_id, cust_id = combo

        print(f"\n--- Forecasting: Product={prod_id}, Location={loc_id}" + (f", Customer={cust_id}" if cust_id else "") + " ---")

        # Filter data for this combination
        filtered = historical_data[
            (historical_data['product_id'] == prod_id) &
            (historical_data['location_id'] == loc_id)
        ].copy()

        if cust_id and 'customer_id' in filtered.columns:
            filtered = filtered[filtered['customer_id'] == cust_id]

        if len(filtered) < 10:  # Need minimum data points
            print(f"⚠️  Skipping: Only {len(filtered)} data points (need at least 10)")
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

        # Group and aggregate
        aggregated = filtered.groupby('date').agg({
            'quantity': 'sum',
            'revenue': 'sum'
        }).reset_index()

        aggregated = aggregated.rename(columns={'quantity': 'value'})
        aggregated = aggregated[['date', 'value']].sort_values('date')

        print(f"   ✓ {len(aggregated)} {time_granularity} periods")

        # Initialize model for this combination
        model_map = {
            'sma': SimpleMovingAverage(),
            'wma': WeightedMovingAverage(),
            'exp-smoothing': ExponentialSmoothing(),
            'holt-winters': HoltWinters(),
            'arima': ARIMAModel(),
            'prophet': ProphetModel()
        }

        if model_type not in model_map:
            print(f"❌ Unknown model type: {model_type}")
            continue

        model = model_map[model_type]

        # Fit model
        try:
            if model_type == 'holt-winters':
                seasonal_periods = min(12 if time_granularity == 'monthly' else 7, len(aggregated) // 2)
                model.fit(aggregated, seasonal_periods=seasonal_periods)
            else:
                model.fit(aggregated)
            print(f"   ✓ Model fitted")
        except Exception as e:
            print(f"   ❌ Error fitting model: {e}")
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
            forecast_df['customer_id'] = cust_id
            all_forecast_data.append(forecast_df)
            forecast_count += 1
            print(f"   ✓ Forecast generated ({periods} periods)")
        except Exception as e:
            print(f"   ❌ Error generating forecast: {e}")
            continue

    if forecast_count == 0:
        print("\n❌ No forecasts were generated!")
        return

    print(f"\n✅ Generated {forecast_count} forecasts successfully")

    # Use first model's parameters for header (they're all the same model type)
    model_map = {
        'sma': SimpleMovingAverage(),
        'wma': WeightedMovingAverage(),
        'exp-smoothing': ExponentialSmoothing(),
        'holt-winters': HoltWinters(),
        'arima': ARIMAModel(),
        'prophet': ProphetModel()
    }
    model = model_map[model_type]

    # Calculate aggregate metrics
    print("\n📊 Calculating aggregate metrics...")

    model_map = {
        'sma': SimpleMovingAverage(),
        'wma': WeightedMovingAverage(),
        'exp-smoothing': ExponentialSmoothing(),
        'holt-winters': HoltWinters(),
        'arima': ARIMAModel(),
        'prophet': ProphetModel()
    }

    if model_type not in model_map:
        print(f"❌ Unknown model type: {model_type}")
        return

    model = model_map[model_type]

    # Fit model
    print("🔧 Fitting model to historical data...")
    try:
        if model_type == 'holt-winters':
            # Detect seasonality
            seasonal_periods = 12 if time_granularity == 'monthly' else 7
            model.fit(aggregated, seasonal_periods=seasonal_periods)
        else:
            model.fit(aggregated)
        print("✓ Model fitted successfully")
    except Exception as e:
        print(f"❌ Error fitting model: {e}")
        return

    # Calculate periods based on granularity
    if time_granularity == 'weekly':
        periods = forecast_horizon_days // 7
    elif time_granularity == 'monthly':
        periods = forecast_horizon_days // 30
    elif time_granularity == 'quarterly':
        periods = forecast_horizon_days // 90
    else:
        periods = forecast_horizon_days

    # Generate forecast
    print(f"\n📈 Generating forecast for {periods} periods...")
    forecast_df = model.predict(periods)
    print(f"✓ Forecast generated")

    # Validate on holdout data
    print("\n📊 Validating model accuracy...")
    test_size = min(30, len(aggregated) // 4)
    metrics = model.validate(aggregated, test_size=test_size)
    print(f"✓ MAPE: {metrics['mape']:.2f}%")
    print(f"✓ MAD: {metrics['mad']:.2f}")
    print(f"✓ RMSE: {metrics['rmse']:.2f}")

    # Save to database
    print("\n💾 Saving forecast to database...")

    forecast_name = f"{model.name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    # Get a valid user_id if not provided
    if not created_by:
        # Query for a user in this tenant
        user_query = f"SELECT id FROM {db.schema_name}.users WHERE tenant_id = :tenant_id LIMIT 1"
        with db.engine.connect() as conn:
            result = conn.execute(text(user_query), {'tenant_id': tenant_id})
            user_row = result.fetchone()
            if user_row:
                created_by = str(user_row[0])
            else:
                print("⚠️  Warning: No user found for tenant. Using NULL for created_by.")
                created_by = None

    forecast_id = db.create_forecast_header(
        tenant_id=tenant_id,
        forecast_name=forecast_name,
        model_type=model_type,
        time_granularity=time_granularity,
        forecast_horizon_days=forecast_horizon_days,
        model_parameters=model.parameters,
        metrics=metrics,
        created_by=created_by
    )

    print(f"✓ Forecast header created: {forecast_id}")

    # Prepare forecast data for insertion
    forecast_data = forecast_df.copy()
    forecast_data['forecast_id'] = forecast_id
    forecast_data['product_id'] = product_id
    forecast_data['location_id'] = location_id
    forecast_data['forecast_date'] = forecast_data['date']
    forecast_data['period_start'] = forecast_data['date']
    forecast_data['period_end'] = forecast_data['date']
    forecast_data['forecasted_quantity'] = forecast_data['forecast']
    forecast_data['forecasted_value'] = None  # Can calculate if needed

    # Select only required columns
    forecast_data = forecast_data[[
        'forecast_id', 'product_id', 'location_id',
        'forecast_date', 'period_start', 'period_end',
        'forecasted_quantity', 'forecasted_value',
        'lower_bound_80', 'upper_bound_80',
        'lower_bound_95', 'upper_bound_95'
    ]]

    db.save_forecast(forecast_id, forecast_data)
    print(f"✓ Saved {len(forecast_data)} forecast records")

    db.close()

    print(f"\n✅ Forecast completed successfully!")
    print(f"Forecast ID: {forecast_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run forecasting models')
    parser.add_argument('--tenant-id', required=True, help='Tenant UUID')
    parser.add_argument('--model', required=True, choices=['sma', 'wma', 'exp-smoothing', 'holt-winters', 'arima', 'prophet'])
    parser.add_argument('--product-id', help='Product UUID (optional)')
    parser.add_argument('--location-id', help='Location UUID (optional)')
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
