import React from 'react';
import './Analytics.css';

const Analytics: React.FC = () => {
  return (
    <div className="analytics">
      <div className="analytics-header">
        <h1>Analytics & Performance</h1>
        <p>Detailed analysis of trading performance and market insights</p>
      </div>
      
      <div className="analytics-grid">
        <div className="analytics-card">
          <h2>Performance Metrics</h2>
          <div className="metrics-grid">
            <div className="metric">
              <span className="metric-label">Win Rate</span>
              <span className="metric-value">73%</span>
            </div>
            <div className="metric">
              <span className="metric-label">Profit Factor</span>
              <span className="metric-value">2.8</span>
            </div>
            <div className="metric">
              <span className="metric-label">Total Return</span>
              <span className="metric-value">+156%</span>
            </div>
            <div className="metric">
              <span className="metric-label">Max Drawdown</span>
              <span className="metric-value">-12%</span>
            </div>
          </div>
        </div>
        
        <div className="analytics-card">
          <h2>Signal Distribution</h2>
          <div className="distribution">
            <div className="dist-item">
              <span className="dist-label">Buy Signals</span>
              <div className="dist-bar">
                <div className="dist-fill buy" style={{width: '65%'}}></div>
              </div>
              <span className="dist-value">65%</span>
            </div>
            <div className="dist-item">
              <span className="dist-label">Sell Signals</span>
              <div className="dist-bar">
                <div className="dist-fill sell" style={{width: '35%'}}></div>
              </div>
              <span className="dist-value">35%</span>
            </div>
          </div>
        </div>
        
        <div className="analytics-card">
          <h2>Top Performing Assets</h2>
          <div className="assets-list">
            <div className="asset-item">
              <span className="asset-name">BTC</span>
              <span className="asset-performance positive">+45%</span>
            </div>
            <div className="asset-item">
              <span className="asset-name">ETH</span>
              <span className="asset-performance positive">+32%</span>
            </div>
            <div className="asset-item">
              <span className="asset-name">ADA</span>
              <span className="asset-performance positive">+28%</span>
            </div>
          </div>
        </div>
        
        <div className="analytics-card">
          <h2>Risk Analysis</h2>
          <div className="risk-metrics">
            <div className="risk-item">
              <span className="risk-label">Sharpe Ratio</span>
              <span className="risk-value">1.85</span>
            </div>
            <div className="risk-item">
              <span className="risk-label">Volatility</span>
              <span className="risk-value">18.5%</span>
            </div>
            <div className="risk-item">
              <span className="risk-label">VaR (95%)</span>
              <span className="risk-value">-8.2%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
