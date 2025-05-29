import React, { useContext } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';

const DoctorDashboard = () => {
  const { user } = useContext(AuthContext);

  return (
    <Container className="mt-4">
      <Row>
        <Col>
          <h2 className="mb-4">Welcome, Dr. {user?.first_name}!</h2>
          <p className="text-muted mb-4">Manage your appointments and profile settings.</p>
        </Col>
      </Row>

      <Row>
        {/* Manage Appointment Slots */}
        <Col md={6} className="mb-4">
          <Card className="h-100">
            <Card.Body className="d-flex flex-column">
              <Card.Title>📅 Appointment Slots</Card.Title>
              <Card.Text>
                Create and manage your available appointment time slots for patients to book.
              </Card.Text>
              <div className="mt-auto">
                <Button 
                  as={Link} 
                  to="/doctor/appointment-slots" 
                  variant="primary" 
                  className="w-100"
                >
                  Manage Slots
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>

        {/* Profile Management */}
        <Col md={6} className="mb-4">
          <Card className="h-100">
            <Card.Body className="d-flex flex-column">
              <Card.Title>👤 My Profile</Card.Title>
              <Card.Text>
                Update your professional information, speciality, working hours, and availability.
              </Card.Text>
              <div className="mt-auto">
                <Button
                  as={Link} 
                  to="/doctor/profile" 
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

export default DoctorDashboard;