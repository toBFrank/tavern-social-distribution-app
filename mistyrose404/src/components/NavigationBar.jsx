import React, { useState } from "react";
import { Link } from 'react-router-dom';
import { Menu, Cottage, Add, Person, Settings } from "@mui/icons-material";
import "../styles/components/NavigationBar.css";

const NavigationBar = () => {
  //#region Variables
  const [expanded, setExpanded] = useState(true);

  const pages = [
    ["Home", <Cottage className="navbar-icon" />, "/"],
    ["Post", <Add className="navbar-icon" />, "/post"],
    ["Profile", <Person className="navbar-icon" />, "/profile"],
    ["Settings", <Settings className="navbar-icon" />, "/settings"]
  ];
  //#endregion

  //#region Functions
  const changeExpanded = () => {
    setExpanded(!expanded);
  };
  //#endregion

  return (
    <nav className="navbar-menu" style={{ width: expanded ? 250 : 50 }}>
      <div className="burger" onClick={changeExpanded}>
        <Menu className="navbar-icon" />
      </div>
      <ul className="navbar-list">
        {pages.map((page, index) => (
            <Link to={page[2]}>
          <li className="navbar-list-item" key={index}>
            <div className="navbar-icon">{page[1]}</div>
            {expanded && (
              <span className="navbar-list-text">
                {page[0]}
              </span>
            )}
          </li>
            </Link>
        ))}
      </ul>
    </nav>
  );
};

export default NavigationBar;