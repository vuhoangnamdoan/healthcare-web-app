import React, { useContext } from 'react';
import { AuthContext } from '../../context/AuthContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBell, faBars } from '@fortawesome/free-solid-svg-icons';
import { Link } from 'react-router-dom';
import { Dropdown, Button } from 'react-bootstrap';

const Header = () => {
  const { user, logout } = useContext(AuthContext);
  return (
    <header className="position-fixed top-0 start-0 end-0 d-flex align-items-center justify-content-between p-4 bg-primary text-white" style={{ zIndex: 1000, height: '70px' }}>
      <div className="header-left">
        <Link to="/" className="text-white text-decoration-none"><h3 className="mb-0 header-title" style={{ fontSize: '1.8rem' }}>Hongnam Hospital</h3></Link>
      </div>
      <div className="header-center">
        <img src="example/path" alt="Hospital Logo" style={{ height: '40px' }} />
      </div>
      <div className="header-right d-flex align-items-center gap-3">
        <span className="me-3" style={{ fontSize: '1.2rem' }}>Hi, {user?.first_name || 'Guest'}</span>
        <Dropdown align="end">
          <Dropdown.Toggle as={Button} variant="link" className="text-white hover-grow me-2 p-0">
            <FontAwesomeIcon icon={faBell} size="lg" />
          </Dropdown.Toggle>
          <Dropdown.Menu style={{ minWidth: '220px' }}>
            <Dropdown.Item>Notification 1</Dropdown.Item>
            <Dropdown.Item>Notification 2</Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
        <Dropdown align="end">
          <Dropdown.Toggle as={Button} variant="link" className="text-white hover-grow p-0">
            <FontAwesomeIcon icon={faBars} size="lg" />
          </Dropdown.Toggle>
          <Dropdown.Menu>
            <Dropdown.Item as={Link} to="/profile">Profile</Dropdown.Item>
            <Dropdown.Item onClick={logout}>Sign Out</Dropdown.Item>
          </Dropdown.Menu>
        </Dropdown>
      </div>
    </header>
  );
};

export default Header;