import React from 'react';
import appLogo from '../assets/Logo.png';
import '../styles/components/TopHeader.css';

const TopHeader = () => {
  return (
    <header className="top-header">
      <img src={appLogo} alt="Logo" className="logo" />
    </header>
  );
};

export default TopHeader;