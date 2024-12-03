import React from 'react';
import '../styles/components/TopNav.css';

const TopNav = () => {
  return (
    <nav className="top-nav">
      <div className="nav-logo">
        <a href="/">MyApp</a>
      </div>
      <ul className="nav-links">
        <li><a href="/home">Home</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/services">Services</a></li>
        <li><a href="/contact">Contact</a></li>
      </ul>
      <div className="nav-burger">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </nav>
  );
};

export default TopNav;