import React, { useState } from 'react';
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

const NavigationBar = () => {
  //#region Variables
  const [expanded, setExpanded] = useState(true);
  const userId = '763f972e-a60f-4233-af4b-1e3408cb5f5b';
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
  //#endregion

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
      <div className="navbar-footer">
        <div className="navbar-icon">
          <MeetingRoomOutlined fontSize="inherit" />
        </div>
        {expanded && <span className="navbar-list-text">Logout</span>}
      </div>
    </nav>
  );
};

export default NavigationBar;
