# Forecast Engine

Python-based statistical forecasting engine for Tessera Cloud.

## Features

- 6 Statistical Models:
  - **Simple Moving Average (SMA)**
  - **Weighted Moving Average (WMA)**
  - **Exponential Smoothing**
  - **Holt-Winters** (with trend and seasonality)
  - **ARIMA** (AutoRegressive Integrated Moving Average)
  - **Prophet** (Facebook's time series forecasting)

- Automatic accuracy metrics calculation (MAPE, MAD, RMSE, Bias, Tracking Signal)
- Confidence intervals (80% and 95%)
- Database integration with PostgreSQL
- Support for multiple time granularities (daily, weekly, monthly, quarterly)

## Setup

1. **Create virtual environment:**
```bash
cd forecast-engine
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

## Usage

### Run a forecast:

```bash
python run_forecast.py \
  --tenant-id <TENANT_UUID> \
  --model exp-smoothing \
  --horizon 90 \
  --granularity monthly
```

### Available models:
- `sma` - Simple Moving Average
- `wma` - Weighted Moving Average
- `exp-smoothing` - Exponential Smoothing
- `holt-winters` - Holt-Winters
- `arima` - ARIMA
- `prophet` - Prophet

### Parameters:
- `--tenant-id` (required): Tenant UUID
- `--model` (required): Model type
- `--product-id` (optional): Filter by product
- `--location-id` (optional): Filter by location
- `--horizon` (optional): Forecast horizon in days (default: 90)
- `--granularity` (optional): daily, weekly, monthly, quarterly (default: daily)
- `--user-id` (optional): User UUID who created the forecast

### Example:

```bash
# Run Holt-Winters forecast for 6 months
python run_forecast.py \
  --tenant-id abc123 \
  --model holt-winters \
  --horizon 180 \
  --granularity monthly

# Run ARIMA forecast for specific product
python run_forecast.py \
  --tenant-id abc123 \
  --model arima \
  --product-id prod456 \
  --horizon 60 \
  --granularity weekly
```

## Project Structure

```
forecast-engine/
├── models/
│   ├── __init__.py
│   ├── base_model.py       # Base class for all models
│   ├── sma.py              # Simple Moving Average
│   ├── wma.py              # Weighted Moving Average
│   ├── exp_smoothing.py    # Exponential Smoothing
│   ├── holt_winters.py     # Holt-Winters
│   ├── arima.py            # ARIMA
│   └── prophet.py          # Prophet
├── utils/
│   ├── __init__.py
│   ├── db_connection.py    # Database utilities
│   └── metrics.py          # Accuracy metrics
├── tests/
│   └── (test files)
├── run_forecast.py         # Main execution script
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## Model Details

### Simple Moving Average
- Window-based average
- Best for: Stable demand patterns
- Parameters: window size

### Weighted Moving Average
- Recent values weighted higher
- Best for: Trending demand
- Parameters: window size, weights

### Exponential Smoothing
- Exponentially weighted average
- Best for: Data with no trend/seasonality
- Parameters: alpha (smoothing level)

### Holt-Winters
- Handles trend and seasonality
- Best for: Seasonal patterns
- Parameters: seasonal_periods, trend type, seasonal type

### ARIMA
- Advanced statistical model
- Best for: Complex patterns
- Parameters: p, d, q orders

### Prophet
- Facebook's robust forecasting
- Best for: Multiple seasonalities, holidays
- Parameters: seasonality flags

## Output

Forecasts are saved to the database with:
- Forecast header (metadata, metrics)
- Detailed forecast values with confidence intervals
- Historical validation metrics

Access forecasts through the Tessera Cloud frontend.
