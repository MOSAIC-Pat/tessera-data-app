import React, { useState } from 'react';
import './SalesAnalytics.css';

interface SalesAnalyticsProps {
  onBack: () => void;
}

type AnalyticsView = 'client' | 'product' | 'sales';

const SalesAnalytics: React.FC<SalesAnalyticsProps> = ({ onBack }) => {
  const [activeView, setActiveView] = useState<AnalyticsView>('client');

  return (
    <div className="sales-analytics-layout">
      <aside className="analytics-sidebar">
        <button onClick={onBack} className="sidebar-back-button">
          ← Dashboard
        </button>

        <nav className="analytics-nav">
          <button
            className={`nav-item ${activeView === 'client' ? 'active' : ''}`}
            onClick={() => setActiveView('client')}
          >
            <span className="nav-icon">👥</span>
            Client Analytics
          </button>
          <button
            className={`nav-item ${activeView === 'product' ? 'active' : ''}`}
            onClick={() => setActiveView('product')}
          >
            <span className="nav-icon">📦</span>
            Product Analytics
          </button>
          <button
            className={`nav-item ${activeView === 'sales' ? 'active' : ''}`}
            onClick={() => setActiveView('sales')}
          >
            <span className="nav-icon">📊</span>
            Sales Analytics
          </button>
        </nav>
      </aside>

      <main className="analytics-main">
        {activeView === 'client' && (
          <div className="analytics-view">
            <h2>Client Analytics</h2>
            <p>Client performance and insights will be displayed here.</p>
          </div>
        )}
        {activeView === 'product' && (
          <div className="analytics-view">
            <h2>Product Analytics</h2>
            <p>Product performance and insights will be displayed here.</p>
          </div>
        )}
        {activeView === 'sales' && (
          <div className="analytics-view">
            <h2>Sales Analytics</h2>
            <p>Sales performance and insights will be displayed here.</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default SalesAnalytics;
