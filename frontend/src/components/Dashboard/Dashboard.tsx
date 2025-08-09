import React, { useState, useEffect } from 'react';
import './Dashboard.css';

interface Signal {
  id: number;
  symbol: string;
  type: 'BUY' | 'SELL';
  confidence: number;
  price: number;
  timestamp: string;
}

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  volume: number;
}

const Dashboard: React.FC = () => {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API calls
    setTimeout(() => {
      setSignals([
        { id: 1, symbol: 'BTC', type: 'BUY', confidence: 85, price: 45000, timestamp: '2024-01-15T10:30:00Z' },
        { id: 2, symbol: 'ETH', type: 'SELL', confidence: 78, price: 3200, timestamp: '2024-01-15T09:15:00Z' },
        { id: 3, symbol: 'ADA', type: 'BUY', confidence: 92, price: 0.45, timestamp: '2024-01-15T08:45:00Z' }
      ]);
      
      setMarketData([
        { symbol: 'BTC', price: 45000, change: 2.5, volume: 2500000000 },
        { symbol: 'ETH', price: 3200, change: -1.2, volume: 1800000000 },
        { symbol: 'ADA', price: 0.45, change: 5.8, volume: 450000000 }
      ]);
      
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) {
    return <div className="loading">Loading Dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>AI Trading Dashboard</h1>
        <p>Real-time signals and market analysis</p>
      </div>

      <div className="dashboard-grid">
        <div className="card signals-card">
          <h2>Recent Signals</h2>
          <div className="signals-list">
            {signals.map(signal => (
              <div key={signal.id} className={`signal-item ${signal.type.toLowerCase()}`}>
                <div className="signal-header">
                  <span className="symbol">{signal.symbol}</span>
                  <span className={`type ${signal.type.toLowerCase()}`}>{signal.type}</span>
                </div>
                <div className="signal-details">
                  <span className="price">${signal.price.toLocaleString()}</span>
                  <span className="confidence">{signal.confidence}% confidence</span>
                </div>
                <div className="signal-time">{new Date(signal.timestamp).toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card market-card">
          <h2>Market Overview</h2>
          <div className="market-list">
            {marketData.map(item => (
              <div key={item.symbol} className="market-item">
                <div className="market-header">
                  <span className="symbol">{item.symbol}</span>
                  <span className={`change ${item.change >= 0 ? 'positive' : 'negative'}`}>
                    {item.change >= 0 ? '+' : ''}{item.change}%
                  </span>
                </div>
                <div className="market-details">
                  <span className="price">${item.price.toLocaleString()}</span>
                  <span className="volume">Vol: ${(item.volume / 1000000).toFixed(1)}M</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card stats-card">
          <h2>Performance Stats</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Win Rate</span>
              <span className="stat-value">73%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Signals</span>
              <span className="stat-value">1,247</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Profit Factor</span>
              <span className="stat-value">2.8</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Max Drawdown</span>
              <span className="stat-value">12%</span>
            </div>
          </div>
        </div>

        <div className="card alerts-card">
          <h2>System Alerts</h2>
          <div className="alerts-list">
            <div className="alert-item info">
              <span className="alert-icon">ℹ️</span>
              <span className="alert-text">New signal generated for BTC</span>
            </div>
            <div className="alert-item success">
              <span className="alert-icon">✅</span>
              <span className="alert-text">Signal executed successfully</span>
            </div>
            <div className="alert-item warning">
              <span className="alert-icon">⚠️</span>
              <span className="alert-text">High volatility detected</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
