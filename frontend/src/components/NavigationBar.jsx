import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  MenuOutlined,
  CottageOutlined,
  AddOutlined,
  PersonOutlined,
  SettingsOutlined,
  MeetingRoomOutlined,
} from '@mui/icons-material';
import '../styles/components/NavigationBar.css';
import Cookies from 'js-cookie';
import appLogo from  '../assets/Logo.png'

const NavigationBar = () => {
  //#region Variables
  const authorId = Cookies.get('author_id');
  const pages = [
    ['Home', <CottageOutlined fontSize="inherit" />, '/'],
    ['Post', <AddOutlined fontSize="inherit" />, '/post'],
    ['Profile', <PersonOutlined fontSize="inherit" />, `/profile/${authorId}`],
    // ['Settings', <SettingsOutlined fontSize="inherit" />, '/settings'],
  ];
  const location = useLocation();
  //#endregion

  //#region Functions

  const handleLogout = () => {
    Cookies.remove('author_id');
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
  };
  //#endregion

  return (
    <nav className="navbar-menu" >
      <ul className="navbar-list">
        {pages.map((page, index) => (
          <Link className="list-link" to={page[2]} key={index}>
            <li
              className={`navbar-list-item${location.pathname === page[2] ? ' current' : ''}`}
              key={index}
            >
              <div className="navbar-icon">{page[1]}</div>
              <span className="navbar-list-text">{page[0]}</span>
            </li>
          </Link>
        ))}
      </ul>
      <div className="navbar-footer" onClick={handleLogout}>
        <div className="navbar-icon">
          <MeetingRoomOutlined fontSize="inherit" />
        </div>
        <span className="navbar-list-text">Logout</span>
      </div>
    </nav>
  );
};

export default NavigationBar;
