import React, { useState } from 'react';
import './SalesForecast.css';

interface SalesForecastProps {
  onBack: () => void;
}

type ForecastModel = 'sma' | 'wma' | 'exp-smoothing' | 'holt-winters' | 'arima' | 'prophet';
type TimeGranularity = 'daily' | 'weekly' | 'monthly' | 'quarterly';
type ForecastHorizon = 30 | 60 | 90 | 180 | 365;

const SalesForecast: React.FC<SalesForecastProps> = ({ onBack }) => {
  const [selectedModel, setSelectedModel] = useState<ForecastModel>('exp-smoothing');
  const [timeGranularity, setTimeGranularity] = useState<TimeGranularity>('monthly');
  const [forecastHorizon, setForecastHorizon] = useState<ForecastHorizon>(90);

  const models = [
    { value: 'sma', label: 'Simple Moving Average' },
    { value: 'wma', label: 'Weighted Moving Average' },
    { value: 'exp-smoothing', label: 'Exponential Smoothing' },
    { value: 'holt-winters', label: 'Holt-Winters' },
    { value: 'arima', label: 'ARIMA' },
    { value: 'prophet', label: 'Prophet' }
  ];

  return (
    <div className="forecast-layout">
      <aside className="forecast-sidebar">
        <button onClick={onBack} className="sidebar-back-button">
          ← Dashboard
        </button>

        <div className="sidebar-section">
          <h3 className="sidebar-title">Model Selection</h3>
          <select
            className="sidebar-select"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value as ForecastModel)}
          >
            {models.map(model => (
              <option key={model.value} value={model.value}>
                {model.label}
              </option>
            ))}
          </select>
        </div>

        <div className="sidebar-section">
          <h3 className="sidebar-title">Time Granularity</h3>
          <div className="radio-group">
            {(['daily', 'weekly', 'monthly', 'quarterly'] as TimeGranularity[]).map(option => (
              <label key={option} className="radio-label">
                <input
                  type="radio"
                  name="granularity"
                  value={option}
                  checked={timeGranularity === option}
                  onChange={(e) => setTimeGranularity(e.target.value as TimeGranularity)}
                />
                <span className="radio-text">{option.charAt(0).toUpperCase() + option.slice(1)}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="sidebar-section">
          <h3 className="sidebar-title">Forecast Horizon</h3>
          <select
            className="sidebar-select"
            value={forecastHorizon}
            onChange={(e) => setForecastHorizon(Number(e.target.value) as ForecastHorizon)}
          >
            <option value={30}>30 Days</option>
            <option value={60}>60 Days</option>
            <option value={90}>90 Days</option>
            <option value={180}>180 Days</option>
            <option value={365}>365 Days</option>
          </select>
        </div>

        <div className="sidebar-section">
          <h3 className="sidebar-title">Filters</h3>
          <select className="sidebar-select">
            <option>All Products</option>
            <option>Product Category A</option>
            <option>Product Category B</option>
          </select>
          <select className="sidebar-select" style={{ marginTop: '10px' }}>
            <option>All Locations</option>
            <option>Location 1</option>
            <option>Location 2</option>
          </select>
        </div>

        <div className="sidebar-section">
          <button className="export-button">Export Forecast</button>
        </div>
      </aside>

      <main className="forecast-main">
        <div className="forecast-content">
          <h2>Sales Forecast</h2>

          {/* Metrics Cards */}
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Forecast Accuracy (MAPE)</div>
              <div className="metric-value">12.3%</div>
              <div className="metric-trend positive">↑ 2.1% improvement</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Mean Absolute Deviation</div>
              <div className="metric-value">156</div>
              <div className="metric-trend negative">↓ 8 units</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Forecast Bias</div>
              <div className="metric-value">-3.2%</div>
              <div className="metric-trend neutral">Stable</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Tracking Signal</div>
              <div className="metric-value">1.8</div>
              <div className="metric-trend positive">Within range</div>
            </div>
          </div>

          {/* Main Chart Area */}
          <div className="chart-container">
            <h3>Forecast vs. Historical Data</h3>
            <div className="chart-placeholder">
              <p>📊 Interactive forecast chart will be displayed here</p>
              <p className="chart-info">
                Model: {models.find(m => m.value === selectedModel)?.label}<br/>
                Granularity: {timeGranularity}<br/>
                Horizon: {forecastHorizon} days
              </p>
            </div>
          </div>

          {/* Model Comparison Table */}
          <div className="model-comparison">
            <h3>Model Performance Comparison</h3>
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Model</th>
                  <th>MAPE</th>
                  <th>MAD</th>
                  <th>RMSE</th>
                  <th>Bias</th>
                </tr>
              </thead>
              <tbody>
                <tr className={selectedModel === 'exp-smoothing' ? 'selected-row' : ''}>
                  <td>Exponential Smoothing</td>
                  <td>12.3%</td>
                  <td>156</td>
                  <td>198</td>
                  <td>-3.2%</td>
                </tr>
                <tr className={selectedModel === 'holt-winters' ? 'selected-row' : ''}>
                  <td>Holt-Winters</td>
                  <td>11.8%</td>
                  <td>149</td>
                  <td>189</td>
                  <td>-2.1%</td>
                </tr>
                <tr className={selectedModel === 'arima' ? 'selected-row' : ''}>
                  <td>ARIMA</td>
                  <td>13.1%</td>
                  <td>168</td>
                  <td>215</td>
                  <td>-4.5%</td>
                </tr>
                <tr className={selectedModel === 'prophet' ? 'selected-row' : ''}>
                  <td>Prophet</td>
                  <td>12.9%</td>
                  <td>163</td>
                  <td>207</td>
                  <td>-3.8%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SalesForecast;
