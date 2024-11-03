// HealthBar.js
import React from 'react';
import './HealthBar.css'; // Create a CSS file for styling

const HealthBar = ({ percentage }) => {
  return (
    <div className="health-bar-container">
      <div className="health-bar" style={{ width: `${percentage}%` }} />
    </div>
  );
};

export default HealthBar;
