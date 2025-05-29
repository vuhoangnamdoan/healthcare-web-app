import React, { useContext } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';

const PatientDashboard = () => {
    const { user } = useContext(AuthContext);

    return (
        <Container className="mt-4">
        <Row>
            <Col>
                <h2 className="mb-4">Welcome, {user?.first_name}!</h2>
                <p className="text-muted mb-4">Manage your healthcare appointments and profile information.</p>
            </Col>
        </Row>

        <Row>
            {/* Browse & Book Appointments */}
            <Col md={6} lg={4} className="mb-4">
                <Card className="h-100">
                    <Card.Body className="d-flex flex-column">
                        <Card.Title>📅 Book Appointment</Card.Title>
                        <Card.Text>
                            Browse available doctors and book appointments based on specialty and availability.
                        </Card.Text>
                        <div className="mt-auto">
                            <Button 
                            as={Link} 
                            to="/patient/appointments/browse" 
                            variant="primary" 
                            className="w-100"
                            >
                                Browse & Book
                            </Button>
                        </div>
                    </Card.Body>
                </Card>
            </Col>

            {/* My Appointments */}
            <Col md={6} lg={4} className="mb-4">
            <Card className="h-100">
                <Card.Body className="d-flex flex-column">
                    <Card.Title>📋 My Appointments</Card.Title>
                    <Card.Text>
                        View your upcoming appointments, appointment history, and cancel bookings if needed.
                    </Card.Text>
                    <div className="mt-auto">
                        <Button 
                        as={Link} 
                        to="/patient/appointments" 
                        variant="primary"  
                        className="w-100"
                        >
                        View Appointments
                        </Button>
                    </div>
                </Card.Body>
            </Card>
            </Col>

            {/* Profile Management */}
            <Col md={6} lg={4} className="mb-4">
            <Card className="h-100">
                <Card.Body className="d-flex flex-column">
                    <Card.Title>👤 My Profile</Card.Title>
                    <Card.Text>
                        Update your personal information, contact details, and emergency contacts.
                    </Card.Text>
                    <div className="mt-auto">
                        <Button 
                        as={Link} 
                        to="/patient/profile" 
                        variant="primary" 
                        className="w-100"
                        >
                        Edit Profile
                        </Button>
                    </div>
                </Card.Body>
            </Card>
            </Col>
        </Row>
        </Container>
    );
};

export default PatientDashboard;