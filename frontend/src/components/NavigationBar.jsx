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

const NavigationBar = () => {
  //#region Variables
  const [expanded, setExpanded] = useState(true);
  const userId = '1d6dfebf-63a6-47a9-8e88-5cda73675db5';
  const pages = [
    ['Home', <CottageOutlined fontSize="inherit" />, '/'],
    ['Post', <AddOutlined fontSize="inherit" />, '/post'],
    ['Profile', <PersonOutlined fontSize="inherit" />, `/profile/${userId}`],
    ['Settings', <SettingsOutlined fontSize="inherit" />, '/settings'],
  ];
  const location = useLocation();
  //#endregion

  //#region Functions
  const changeExpanded = () => {
    setExpanded(!expanded);
  };

  const handleLogout = () => {
    Cookies.remove('author_id');
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
  };
  //#endregion

  // hide navigation bar if user is not authenticated
  return (
    <nav className="navbar-menu" style={{ width: expanded ? 300 : 150 }}>
      <div className={`navbar-header${expanded ? '' : ' minimized'}`}>
        {expanded && <span className="navbar-title">Tavern</span>}
        <div className="burger" onClick={changeExpanded}>
          <div className="navbar-icon">
            <MenuOutlined fontSize="inherit" />
          </div>
        </div>
      </div>
      <ul className="navbar-list">
        {pages.map((page, index) => (
          <Link className="list-link" to={page[2]} key={index}>
            <li
              className={`navbar-list-item${location.pathname === page[2] ? ' current' : ''}${expanded ? '' : ' minimized'}`}
              key={index}
            >
              <div className="navbar-icon">{page[1]}</div>
              {expanded && <span className="navbar-list-text">{page[0]}</span>}
            </li>
          </Link>
        ))}
      </ul>
      <div className="navbar-footer" onClick={handleLogout}>
        <div className="navbar-icon">
          <MeetingRoomOutlined fontSize="inherit" />
        </div>
        {expanded && <span className="navbar-list-text">Logout</span>}
      </div>
    </nav>
  );
};

export default NavigationBar;
