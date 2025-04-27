import React from 'react';
import { Link } from 'react-router-dom';

const Sidebar = () => (
  <div
    className="sidebar p-4 bg-light"
    style={{
      position: 'fixed',
      top: '70px',
      left: 0,
      height: '100vh',
      width: '280px',
      overflowY: 'auto',
      zIndex: 500     // lower than header/footer
    }}
  >
    <h5 className="mb-4" style={{ fontSize: '1.5rem' }}>NAVIGATION</h5>
    <Link to="/appointments/booking" className="btn btn-outline-primary rounded-pill w-100 mb-3 sidebar-button" style={{ fontSize: '1.1rem' }}>
      Booking
    </Link>
    <Link to="/appointments/calendar" className="btn btn-outline-primary rounded-pill w-100 mb-3 sidebar-button" style={{ fontSize: '1.1rem' }}>
      Calendar
    </Link>
    <Link to="/doctors" className="btn btn-outline-primary rounded-pill w-100 mb-3 sidebar-button" style={{ fontSize: '1.1rem' }}>
      Doctor List
    </Link>
  </div>
);

export default Sidebar;