-- Forecast Schema for Tessera Cloud
-- Excludes historical_sales (using existing tenant_sales table)

-- 1. Main forecast header table
CREATE TABLE raw_tenant_data.forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES raw_tenant_data.tenants(id) ON DELETE CASCADE,
    forecast_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'sma', 'wma', 'exp-smoothing', 'holt-winters', 'arima', 'prophet'
    time_granularity VARCHAR(20) NOT NULL, -- 'daily', 'weekly', 'monthly', 'quarterly'
    forecast_horizon_days INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'approved', 'archived'
    created_by UUID REFERENCES raw_tenant_data.users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Model parameters (stored as JSONB for flexibility)
    model_parameters JSONB, -- e.g., {"alpha": 0.3, "seasonality": "additive"}

    -- Accuracy metrics
    mape DECIMAL(10,4), -- Mean Absolute Percentage Error
    mad DECIMAL(10,2),  -- Mean Absolute Deviation
    rmse DECIMAL(10,2), -- Root Mean Square Error
    bias DECIMAL(10,4), -- Forecast bias
    tracking_signal DECIMAL(10,4)
);

CREATE INDEX idx_forecasts_tenant ON raw_tenant_data.forecasts(tenant_id);
CREATE INDEX idx_forecasts_created ON raw_tenant_data.forecasts(created_at);
CREATE INDEX idx_forecasts_status ON raw_tenant_data.forecasts(status);

-- 2. Detailed forecast values
CREATE TABLE raw_tenant_data.forecast_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forecast_id UUID NOT NULL REFERENCES raw_tenant_data.forecasts(id) ON DELETE CASCADE,

    -- Dimension keys
    product_id UUID, -- References products table
    location_id UUID, -- References locations table
    customer_id UUID, -- References customers table (optional)

    -- Time dimension
    forecast_date DATE NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Forecast values
    forecasted_quantity DECIMAL(15,2) NOT NULL,
    forecasted_value DECIMAL(15,2), -- Dollar value

    -- Confidence intervals
    lower_bound_80 DECIMAL(15,2), -- 80% confidence lower
    upper_bound_80 DECIMAL(15,2), -- 80% confidence upper
    lower_bound_95 DECIMAL(15,2), -- 95% confidence lower
    upper_bound_95 DECIMAL(15,2), -- 95% confidence upper

    -- Actuals (filled in after the period)
    actual_quantity DECIMAL(15,2),
    actual_value DECIMAL(15,2),

    -- Variance metrics
    variance_quantity DECIMAL(15,2), -- actual - forecast
    variance_pct DECIMAL(10,4),      -- (actual - forecast) / forecast

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_forecast_data_forecast ON raw_tenant_data.forecast_data(forecast_id);
CREATE INDEX idx_forecast_data_product ON raw_tenant_data.forecast_data(product_id);
CREATE INDEX idx_forecast_data_location ON raw_tenant_data.forecast_data(location_id);
CREATE INDEX idx_forecast_data_customer ON raw_tenant_data.forecast_data(customer_id);
CREATE INDEX idx_forecast_data_date ON raw_tenant_data.forecast_data(forecast_date);
CREATE INDEX idx_forecast_data_period ON raw_tenant_data.forecast_data(period_start, period_end);

-- 3. Model configurations
CREATE TABLE raw_tenant_data.forecast_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES raw_tenant_data.tenants(id) ON DELETE CASCADE,

    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,

    -- Model configuration
    config JSONB NOT NULL, -- All model-specific parameters

    -- Performance tracking
    avg_mape DECIMAL(10,4),
    avg_mad DECIMAL(10,2),
    last_trained TIMESTAMP,

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_forecast_models_tenant ON raw_tenant_data.forecast_models(tenant_id);
CREATE INDEX idx_forecast_models_type ON raw_tenant_data.forecast_models(model_type);

-- 4. Manual overrides/adjustments
CREATE TABLE raw_tenant_data.forecast_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forecast_data_id UUID REFERENCES raw_tenant_data.forecast_data(id) ON DELETE CASCADE,

    original_value DECIMAL(15,2) NOT NULL,
    adjusted_value DECIMAL(15,2) NOT NULL,
    adjustment_reason TEXT,

    adjusted_by UUID REFERENCES raw_tenant_data.users(id),
    adjusted_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_forecast_adjustments_data ON raw_tenant_data.forecast_adjustments(forecast_data_id);
CREATE INDEX idx_forecast_adjustments_user ON raw_tenant_data.forecast_adjustments(adjusted_by);

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_forecasts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Trigger for forecasts table
CREATE TRIGGER update_forecasts_timestamp
    BEFORE UPDATE ON raw_tenant_data.forecasts
    FOR EACH ROW
    EXECUTE FUNCTION update_forecasts_updated_at();

-- Comments for documentation
COMMENT ON TABLE raw_tenant_data.forecasts IS 'Main forecast header table containing forecast metadata and accuracy metrics';
COMMENT ON TABLE raw_tenant_data.forecast_data IS 'Detailed forecast values with confidence intervals and actual comparisons';
COMMENT ON TABLE raw_tenant_data.forecast_models IS 'Saved model configurations and performance tracking';
COMMENT ON TABLE raw_tenant_data.forecast_adjustments IS 'Manual adjustments to forecasts with audit trail';
