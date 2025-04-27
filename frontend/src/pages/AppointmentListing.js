import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Badge, Modal, Spinner, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import Layout from '../components/layout/Layout';
import { getUserAppointments, cancelAppointment } from '../services/appointmentService';

const AppointmentListing = () => {
  const navigate = useNavigate();
  
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // For cancellation confirmation
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [cancelling, setCancelling] = useState(false);
  const [cancelSuccess, setCancelSuccess] = useState('');
  
  // Fetch user appointments
  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        setLoading(true);
        setError('');
        
        const data = await getUserAppointments();
        setAppointments(data);
      } catch (err) {
        console.error('Error fetching appointments:', err);
        setError('Failed to load your appointments. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchAppointments();
  }, []);
  
  // Helper to get status badge
  const getStatusBadge = (status) => {
    switch (status?.toUpperCase()) {
      case 'SCHEDULED':
        return <Badge bg="primary">Scheduled</Badge>;
      case 'COMPLETED':
        return <Badge bg="success">Completed</Badge>;
      case 'CANCELLED':
        return <Badge bg="danger">Cancelled</Badge>;
      case 'NO_SHOW':
        return <Badge bg="warning" text="dark">No Show</Badge>;
      case 'IN_PROGRESS':
        return <Badge bg="info">In Progress</Badge>;
      default:
        return <Badge bg="secondary">Unknown</Badge>;
    }
  };
  
  // Format the appointment date and time for display
  const formatDateTime = (dateTimeStr) => {
    try {
      const dateTime = new Date(dateTimeStr);
      return format(dateTime, 'MMM dd, yyyy h:mm a');
    } catch (error) {
      console.error('Error formatting date:', error);
      return dateTimeStr;
    }
  };
  
  // Handle view appointment details
  const handleViewDetails = (appointmentId) => {
    navigate(`/appointments/${appointmentId}`);
  };
  
  // Handle reschedule appointment
  const handleReschedule = (appointment) => {
    navigate(`/appointments/reschedule/${appointment.id}`, { 
      state: { appointment } 
    });
  };
  
  // Open cancellation modal
  const handleCancelClick = (appointment) => {
    setSelectedAppointment(appointment);
    setShowConfirmModal(true);
  };
  
  // Close cancellation modal
  const handleCloseModal = () => {
    setShowConfirmModal(false);
    setSelectedAppointment(null);
  };
  
  // Confirm appointment cancellation
  const handleConfirmCancel = async () => {
    if (!selectedAppointment) return;
    
    try {
      setCancelling(true);
      await cancelAppointment(selectedAppointment.id);
      
      // Update the local appointments list
      setAppointments(appointments.map(app => 
        app.id === selectedAppointment.id ? { ...app, status: 'CANCELLED' } : app
      ));
      
      setCancelSuccess(`Appointment with Dr. ${selectedAppointment.doctor_name} has been cancelled.`);
      setTimeout(() => setCancelSuccess(''), 5000); // Clear success message after 5 seconds
    } catch (err) {
      console.error('Error cancelling appointment:', err);
      setError('Failed to cancel appointment. Please try again later.');
    } finally {
      setCancelling(false);
      handleCloseModal();
    }
  };
  
  // Handle booking a new appointment
  const handleBookNew = () => {
    navigate('/appointments/book');
  };

  return (
    <Layout>
      <Container className="mt-4">
        <Row className="mb-4">
          <Col>
            <h2 className="mb-0">My Appointments</h2>
          </Col>
          <Col xs="auto">
            <Button variant="primary" onClick={handleBookNew}>
              Book New Appointment
            </Button>
          </Col>
        </Row>
        
        {error && <Alert variant="danger">{error}</Alert>}
        {cancelSuccess && <Alert variant="success">{cancelSuccess}</Alert>}
        
        <Card>
          <Card.Body>
            {loading ? (
              <div className="text-center py-5">
                <Spinner animation="border" role="status" variant="primary" />
                <p className="mt-2">Loading your appointments...</p>
              </div>
            ) : appointments.length === 0 ? (
              <div className="text-center py-5">
                <p className="mb-3">You don't have any appointments yet.</p>
                <Button variant="primary" onClick={handleBookNew}>
                  Book Your First Appointment
                </Button>
              </div>
            ) : (
              <div className="table-responsive">
                <Table hover>
                  <thead>
                    <tr>
                      <th>Doctor</th>
                      <th>Date & Time</th>
                      <th>Reason</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {appointments.map((appointment) => (
                      <tr key={appointment.id}>
                        <td>Dr. {appointment.doctor_name}</td>
                        <td>{formatDateTime(appointment.appointment_datetime)}</td>
                        <td>{appointment.reason || 'Not specified'}</td>
                        <td>{getStatusBadge(appointment.status)}</td>
                        <td>
                          <div className="d-flex gap-2">
                            <Button 
                              variant="outline-primary" 
                              size="sm"
                              onClick={() => handleViewDetails(appointment.id)}
                            >
                              Details
                            </Button>
                            
                            {appointment.status === 'SCHEDULED' && (
                              <>
                                <Button 
                                  variant="outline-secondary" 
                                  size="sm"
                                  onClick={() => handleReschedule(appointment)}
                                >
                                  Reschedule
                                </Button>
                                <Button 
                                  variant="outline-danger" 
                                  size="sm"
                                  onClick={() => handleCancelClick(appointment)}
                                >
                                  Cancel
                                </Button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            )}
          </Card.Body>
        </Card>
        
        {/* Cancel Confirmation Modal */}
        <Modal show={showConfirmModal} onHide={handleCloseModal} centered>
          <Modal.Header closeButton>
            <Modal.Title>Cancel Appointment</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {selectedAppointment && (
              <p>
                Are you sure you want to cancel your appointment with 
                Dr. {selectedAppointment.doctor_name} on {formatDateTime(selectedAppointment.appointment_datetime)}?
              </p>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal} disabled={cancelling}>
              No, Keep It
            </Button>
            <Button 
              variant="danger" 
              onClick={handleConfirmCancel}
              disabled={cancelling}
            >
              {cancelling ? (
                <>
                  <Spinner animation="border" size="sm" className="me-2" />
                  Cancelling...
                </>
              ) : (
                'Yes, Cancel Appointment'
              )}
            </Button>
          </Modal.Footer>
        </Modal>
      </Container>
    </Layout>
  );
};

export default AppointmentListing;