import React, { useContext } from 'react';
import { Navbar as BootstrapNavbar, Nav, Container, Dropdown } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Navbar = () => {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/auth/login');
    };

    if (!user) {
        return null; // Don't show navbar if user is not logged in
    }

    return (
        <BootstrapNavbar bg="primary" variant="dark" expand="lg" className="mb-0">
            <Container>
                <BootstrapNavbar.Brand as={Link} to="/">
                🏥 Hong Nam Healthcare System
                </BootstrapNavbar.Brand>
                <BootstrapNavbar.Toggle aria-controls="basic-navbar-nav" />
                <BootstrapNavbar.Collapse id="basic-navbar-nav">
                <Nav className="me-auto">
                    {user.role === 'patient' && (
                    <>
                        <Nav.Link as={Link} to="/patient/dashboard">Home</Nav.Link>
                        <Nav.Link as={Link} to="/patient/appointments/browse">Book Appointment</Nav.Link>
                        <Nav.Link as={Link} to="/patient/appointments">My Bookings</Nav.Link>
                    </>
                    )}
                    
                    {user.role === 'doctor' && (
                    <>
                        <Nav.Link as={Link} to="/doctor/dashboard">Home</Nav.Link>
                        <Nav.Link as={Link} to="/doctor/appointment-slots">Appointment Slots</Nav.Link>
                    </>
                    )}
                </Nav>
                <Nav className="ms-auto">
                    <Dropdown align="end">
                    <Dropdown.Toggle variant="outline-light" id="user-dropdown">
                        {user.first_name} {user.last_name}
                    </Dropdown.Toggle>
                    <Dropdown.Menu>
                        <Dropdown.Header>
                            <strong>{user.first_name} {user.last_name}</strong>
                            <br />
                            <small className="text-muted">{user.email}</small>
                            <br />
                            <small className="text-muted">{user.role}</small>
                        </Dropdown.Header>
                        <Dropdown.Divider />
                            <Dropdown.Item as={Link} to={user.role === 'patient' ? '/patient/profile' : '/doctor/profile'}>
                                Edit Profile
                            </Dropdown.Item>
                        <Dropdown.Divider />
                        <Dropdown.Item onClick={handleLogout} className="text-danger">
                            Logout
                        </Dropdown.Item>
                    </Dropdown.Menu>
                    </Dropdown>
                </Nav>
                </BootstrapNavbar.Collapse>
            </Container>
        </BootstrapNavbar>
    );
};

export default Navbar;