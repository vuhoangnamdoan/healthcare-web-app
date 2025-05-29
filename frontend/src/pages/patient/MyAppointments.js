import React, { useState, useEffect, useCallback } from 'react';
import { 
    Container, Row, Col, Card, Badge, Button, Alert, 
    Spinner, Modal, Form, Table, InputGroup
} from 'react-bootstrap';
import { appointmentAPI } from '../../services/api';

const MyAppointments = () => {
    const [bookings, setBookings] = useState([]);
    const [filteredBookings, setFilteredBookings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    
    const [filterStatus, setFilterStatus] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');
    
    const [showCancelModal, setShowCancelModal] = useState(false);
    const [selectedBooking, setSelectedBooking] = useState(null);
    const [cancellationReason, setCancellationReason] = useState('');
    const [cancelLoading, setCancelLoading] = useState(false);

    const fetchMyBookings = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await appointmentAPI.getMyBookings();
            const bookingsData = Array.isArray(response.data) ? response.data : 
                              (response.data.results ? response.data.results : []);
            
            setBookings(bookingsData);
        } catch (err) {
            setError('Failed to load your appointments. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const filterBookings = useCallback(() => {
        let filtered = bookings;

        if (filterStatus === 'active') {
            filtered = filtered.filter(booking => !booking.is_canceled);
        } else if (filterStatus === 'canceled') {
            filtered = filtered.filter(booking => booking.is_canceled);
        }

        if (searchTerm) {
            filtered = filtered.filter(booking => {
                const doctorName = `${booking.appointment_info?.doctor_info?.user?.first_name || ''} ${booking.appointment_info?.doctor_info?.user?.last_name || ''}`.toLowerCase();
                const specialty = booking.appointment_info?.doctor_info?.speciality?.toLowerCase() || '';
                const reason = booking.reason?.toLowerCase() || '';
                
                return doctorName.includes(searchTerm.toLowerCase()) ||
                       specialty.includes(searchTerm.toLowerCase()) ||
                       reason.includes(searchTerm.toLowerCase());
            });
        }

        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setFilteredBookings(filtered);
    }, [bookings, filterStatus, searchTerm]);

    useEffect(() => {
        fetchMyBookings();
    }, []);

    useEffect(() => {
        filterBookings();
    }, [filterBookings]);

    const handleCancelBooking = (booking) => {
        setSelectedBooking(booking);
        setShowCancelModal(true);
        setCancellationReason('');
    };

    const confirmCancelBooking = async () => {
        if (!selectedBooking) return;

        setCancelLoading(true);
        setError('');

        try {
            await appointmentAPI.cancelBooking(selectedBooking.booking_id, {
                cancellation_reason: cancellationReason.trim() || 'Canceled by patient'
            });

            setSuccess('Appointment canceled successfully.');
            setShowCancelModal(false);
            setSelectedBooking(null);
            setCancellationReason('');
            
            fetchMyBookings();
        } catch (err) {
            const errorMsg = err.response?.data?.detail || 
                          err.response?.data?.message ||
                          'Failed to cancel appointment. Please try again.';
            setError(errorMsg);
        } finally {
            setCancelLoading(false);
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    const formatTime = (timeString) => {
        return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    };

    const getStatusBadge = (booking) => {
        if (booking.is_canceled) {
            return <Badge bg="danger">Canceled</Badge>;
        }
        return <Badge bg="success">Active</Badge>;
    };

    if (loading) {
        return (
            <Container className="mt-4">
                <div className="text-center py-5">
                    <Spinner animation="border" role="status">
                        <span className="visually-hidden">Loading your appointments...</span>
                    </Spinner>
                    <p className="mt-2">Loading your appointments...</p>
                </div>
            </Container>
        );
    }

    return (
        <Container className="mt-4">
            <Row>
                <Col>
                    <div className="d-flex justify-content-between align-items-center mb-4">
                        <h2>My Appointments</h2>
                        <Button 
                            variant="primary" 
                            href="/patient/appointments/browse"
                            className="ms-auto"
                        >
                            Book New Appointment
                        </Button>
                    </div>

                    {success && (
                        <Alert variant="success" dismissible onClose={() => setSuccess('')}>
                            {success}
                        </Alert>
                    )}
                    
                    {error && (
                        <Alert variant="danger" dismissible onClose={() => setError('')}>
                            {error}
                        </Alert>
                    )}

                    <Card className="mb-4">
                        <Card.Body>
                            <Row>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Search Appointments</Form.Label>
                                        <InputGroup>
                                            <Form.Control
                                                type="text"
                                                placeholder="Search by doctor name, specialty, or reason..."
                                                value={searchTerm}
                                                onChange={(e) => setSearchTerm(e.target.value)}
                                            />
                                        </InputGroup>
                                    </Form.Group>
                                </Col>
                                <Col md={6}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Filter by Status</Form.Label>
                                        <Form.Select
                                            value={filterStatus}
                                            onChange={(e) => setFilterStatus(e.target.value)}
                                        >
                                            <option value="all">All Appointments</option>
                                            <option value="active">Active Appointments</option>
                                            <option value="canceled">Canceled Appointments</option>
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                            </Row>
                        </Card.Body>
                    </Card>

                    {filteredBookings.length === 0 ? (
                        <Alert variant="info">
                            {bookings.length === 0 
                                ? "You haven't booked any appointments yet." 
                                : "No appointments found matching your search criteria."
                            }
                            {bookings.length === 0 && (
                                <div className="mt-3">
                                    <Button variant="primary" href="/patient/appointments/browse">
                                        Book Your First Appointment
                                    </Button>
                                </div>
                            )}
                        </Alert>
                    ) : (
                        <>
                            <Card className="mb-4">
                                <Card.Body>
                                    <Row className="text-center">
                                        <Col md={4}>
                                            <h4 className="text-primary">
                                                {bookings.filter(b => !b.is_canceled).length}
                                            </h4>
                                            <p className="text-muted mb-0">Active Appointments</p>
                                        </Col>
                                        <Col md={4}>
                                            <h4 className="text-success">
                                                {bookings.length}
                                            </h4>
                                            <p className="text-muted mb-0">Total Bookings</p>
                                        </Col>
                                        <Col md={4}>
                                            <h4 className="text-danger">
                                                {bookings.filter(b => b.is_canceled).length}
                                            </h4>
                                            <p className="text-muted mb-0">Canceled</p>
                                        </Col>
                                    </Row>
                                </Card.Body>
                            </Card>

                            <Card>
                                <Card.Body className="p-0">
                                    <Table responsive className="mb-0">
                                        <thead className="table-light">
                                            <tr>
                                                <th>Doctor</th>
                                                <th>Specialty</th>
                                                <th>Date & Time</th>
                                                <th>Reason</th>
                                                <th>Status</th>
                                                <th>Booked On</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {filteredBookings.map(booking => (
                                                <tr key={booking.booking_id}>
                                                    <td>
                                                        <div>
                                                            <strong>
                                                                Dr. {booking.appointment_info?.doctor_info?.user?.first_name} {booking.appointment_info?.doctor_info?.user?.last_name}
                                                            </strong>
                                                            <br />
                                                            <small className="text-muted">
                                                                {booking.appointment_info?.doctor_info?.experience} years experience
                                                            </small>
                                                        </div>
                                                    </td>
                                                    <td>
                                                        <Badge bg="primary" className="me-1">
                                                            {booking.appointment_info?.doctor_info?.speciality}
                                                        </Badge>
                                                    </td>
                                                    <td>
                                                        <div>
                                                            <strong>{booking.appointment_info?.week_day_display}</strong>
                                                            <br />
                                                            <span className="text-muted">
                                                                {formatTime(booking.appointment_info?.start_time)} - {formatTime(booking.appointment_info?.end_time)}
                                                            </span>
                                                            <br />
                                                            <small className="text-muted">
                                                                ({booking.appointment_info?.duration} minutes)
                                                            </small>
                                                        </div>
                                                    </td>
                                                    <td>
                                                        <div style={{ maxWidth: '200px' }}>
                                                            {booking.reason ? (
                                                                <span className="text-truncate d-inline-block" style={{ maxWidth: '100%' }}>
                                                                    {booking.reason}
                                                                </span>
                                                            ) : (
                                                                <span className="text-muted">No reason provided</span>
                                                            )}
                                                        </div>
                                                    </td>
                                                    <td>
                                                        {getStatusBadge(booking)}
                                                        {booking.is_canceled && booking.canceled_at && (
                                                            <div>
                                                                <small className="text-muted">
                                                                    {formatDate(booking.canceled_at)}
                                                                </small>
                                                            </div>
                                                        )}
                                                    </td>
                                                    <td>
                                                        <small className="text-muted">
                                                            {formatDate(booking.created_at)}
                                                        </small>
                                                    </td>
                                                    <td>
                                                        {!booking.is_canceled ? (
                                                            <Button
                                                                variant="outline-danger"
                                                                size="sm"
                                                                onClick={() => handleCancelBooking(booking)}
                                                            >
                                                                Cancel
                                                            </Button>
                                                        ) : (
                                                            <span className="text-muted">-</span>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </Table>
                                </Card.Body>
                            </Card>
                        </>
                    )}
                </Col>
            </Row>

            <Modal show={showCancelModal} onHide={() => setShowCancelModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>Cancel Appointment</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {selectedBooking && (
                        <div>
                            <h6>Are you sure you want to cancel this appointment?</h6>
                            <div className="bg-light p-3 rounded mb-3">
                                <strong>Doctor:</strong> Dr. {selectedBooking.appointment_info?.doctor_info?.user?.first_name} {selectedBooking.appointment_info?.doctor_info?.user?.last_name}<br />
                                <strong>Specialty:</strong> {selectedBooking.appointment_info?.doctor_info?.speciality}<br />
                                <strong>Date & Time:</strong> {selectedBooking.appointment_info?.week_day_display} at {formatTime(selectedBooking.appointment_info?.start_time)}<br />
                                <strong>Duration:</strong> {selectedBooking.appointment_info?.duration} minutes
                            </div>
                            
                            <Form.Group>
                                <Form.Label>Reason for Cancellation (Optional)</Form.Label>
                                <Form.Control
                                    as="textarea"
                                    rows={3}
                                    placeholder="Please let us know why you're canceling..."
                                    value={cancellationReason}
                                    onChange={(e) => setCancellationReason(e.target.value)}
                                    maxLength={500}
                                />
                                <Form.Text className="text-muted">
                                    {cancellationReason.length}/500 characters
                                </Form.Text>
                            </Form.Group>
                        </div>
                    )}
                </Modal.Body>
                <Modal.Footer>
                    <Button 
                        variant="secondary" 
                        onClick={() => setShowCancelModal(false)}
                        disabled={cancelLoading}
                    >
                        Keep Appointment
                    </Button>
                    <Button 
                        variant="danger" 
                        onClick={confirmCancelBooking}
                        disabled={cancelLoading}
                    >
                        {cancelLoading ? (
                            <>
                                <Spinner
                                    as="span"
                                    animation="border"
                                    size="sm"
                                    role="status"
                                    className="me-2"
                                />
                                Canceling...
                            </>
                        ) : (
                            'Cancel Appointment'
                        )}
                    </Button>
                </Modal.Footer>
            </Modal>
        </Container>
    );
};

export default MyAppointments;