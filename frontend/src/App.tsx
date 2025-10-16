import { useState, useEffect } from 'react';
import Login from './components/Login';
import SalesAnalytics from './components/SalesAnalytics';
import './App.css';

interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
}

type ActiveModule = 'dashboard' | 'sales-analytics' | 'sales-forecast' | 'demand-planning' | 'settings';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeModule, setActiveModule] = useState<ActiveModule>('dashboard');

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');

    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Error parsing saved user:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData: User) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setActiveModule('dashboard');
  };

  if (loading) {
    return <div className="loading-app">Loading...</div>;
  }

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-left">
          <h1>Tessera Cloud</h1>
        </div>
        <div className="user-info">
          <span>Welcome, {user.firstName} {user.lastName}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </header>
      <main className="app-main">
        {activeModule === 'dashboard' && (
          <div className="main-container">
            <h2>Welcome to Tessera Cloud</h2>
            <p>You are successfully logged in!</p>

            <div className="modules-grid">
              <div className="module-card" onClick={() => setActiveModule('sales-forecast')}>
                <h3>Sales Forecast</h3>
                <p>Predict future sales trends and patterns</p>
              </div>
              <div className="module-card" onClick={() => setActiveModule('demand-planning')}>
                <h3>Demand Planning</h3>
                <p>Optimize inventory and resource allocation</p>
              </div>
              <div className="module-card" onClick={() => setActiveModule('sales-analytics')}>
                <h3>Sales Analytics</h3>
                <p>Analyze sales performance and insights</p>
              </div>
              <div className="module-card" onClick={() => setActiveModule('settings')}>
                <h3>Settings</h3>
                <p>Configure your account and preferences</p>
              </div>
            </div>
          </div>
        )}

        {activeModule === 'sales-analytics' && (
          <SalesAnalytics onBack={() => setActiveModule('dashboard')} />
        )}

        {activeModule === 'sales-forecast' && (
          <div className="main-container">
            <button onClick={() => setActiveModule('dashboard')} className="back-button">
              ← Back to Dashboard
            </button>
            <h2>Sales Forecast</h2>
            <p>Sales forecast module coming soon...</p>
          </div>
        )}

        {activeModule === 'demand-planning' && (
          <div className="main-container">
            <button onClick={() => setActiveModule('dashboard')} className="back-button">
              ← Back to Dashboard
            </button>
            <h2>Demand Planning</h2>
            <p>Demand planning module coming soon...</p>
          </div>
        )}

        {activeModule === 'settings' && (
          <div className="main-container">
            <button onClick={() => setActiveModule('dashboard')} className="back-button">
              ← Back to Dashboard
            </button>
            <h2>Settings</h2>
            <p>Settings module coming soon...</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
