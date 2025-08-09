import React from 'react';
import './Signals.css';

const Signals: React.FC = () => {
  return (
    <div className="signals">
      <div className="signals-header">
        <h1>Trading Signals</h1>
        <p>AI-generated trading signals with confidence scores</p>
      </div>
      
      <div className="signals-content">
        <div className="signal-filters">
          <button className="filter-btn active">All Signals</button>
          <button className="filter-btn">Buy Signals</button>
          <button className="filter-btn">Sell Signals</button>
          <button className="filter-btn">High Confidence</button>
        </div>
        
        <div className="signals-grid">
          <div className="signal-card buy">
            <div className="signal-header">
              <span className="symbol">BTC</span>
              <span className="type buy">BUY</span>
            </div>
            <div className="signal-body">
              <div className="price">$45,000</div>
              <div className="confidence">85% Confidence</div>
              <div className="target">Target: $48,500</div>
              <div className="stop-loss">Stop Loss: $43,200</div>
            </div>
            <div className="signal-footer">
              <span className="time">2 hours ago</span>
              <span className="status active">Active</span>
            </div>
          </div>
          
          <div className="signal-card sell">
            <div className="signal-header">
              <span className="symbol">ETH</span>
              <span className="type sell">SELL</span>
            </div>
            <div className="signal-body">
              <div className="price">$3,200</div>
              <div className="confidence">78% Confidence</div>
              <div className="target">Target: $2,950</div>
              <div className="stop-loss">Stop Loss: $3,350</div>
            </div>
            <div className="signal-footer">
              <span className="time">4 hours ago</span>
              <span className="status active">Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signals;
