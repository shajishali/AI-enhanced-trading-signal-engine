import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" className="navbar-logo">
          🚀 AI Trading Engine
        </Link>
      </div>
      <div className="navbar-menu">
        <Link to="/" className="navbar-item">Dashboard</Link>
        <Link to="/signals" className="navbar-item">Signals</Link>
        <Link to="/analytics" className="navbar-item">Analytics</Link>
        <Link to="/login" className="navbar-item">Login</Link>
      </div>
    </nav>
  );
};

export default Navbar;
