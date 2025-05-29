import React, { useState, useEffect, useContext } from 'react';
import { 
  Container, Row, Col, Card, Button, Form, Modal, Alert, 
  Spinner, Badge, InputGroup 
} from 'react-bootstrap';
import { userAPI, appointmentAPI } from '../../services/api';
import { AuthContext } from '../../context/AuthContext';

const AppointmentBrowser = () => {
    const [doctors, setDoctors] = useState([]);
    const [filteredDoctors, setFilteredDoctors] = useState([]);
    const [selectedDoctor, setSelectedDoctor] = useState(null);
    const [availableSlots, setAvailableSlots] = useState([]);
    const [selectedSlot, setSelectedSlot] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedSpecialty, setSelectedSpecialty] = useState('');
    const [reason, setReason] = useState('');
    
    const [loading, setLoading] = useState(false);
    const [slotsLoading, setSlotsLoading] = useState(false);
    const [bookingLoading, setBookingLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    
    const [showSlotsModal, setShowSlotsModal] = useState(false);
    const [showBookingModal, setShowBookingModal] = useState(false);
    
    const { user } = useContext(AuthContext);

    const specialties = [
        { value: '', label: 'All Specialties' },
        { value: 'Mental', label: 'Mental Health' },
        { value: 'General', label: 'General Medicine' },
        { value: 'Density', label: 'Dentistry' },
        { value: 'Physiotherapy', label: 'Physiotherapy' },
        { value: 'Chiropractic', label: 'Chiropractic' },
        { value: 'Audiology', label: 'Audiology' },
        { value: 'Optometry', label: 'Optometry' },
    ];

    useEffect(() => {
        fetchDoctors();
    }, []);

    const fetchDoctors = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await userAPI.getDoctors();
            const doctorsData = Array.isArray(response.data) ? response.data : (response.data.results ? response.data.results : []);
            setDoctors(doctorsData);
            setFilteredDoctors(doctorsData);
        } catch (err) {
            setError('Failed to load doctors. Please try again.');
            setDoctors([]);
            setFilteredDoctors([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!Array.isArray(doctors)) {
            setFilteredDoctors([]);
            return;
        }

        let filtered = doctors;

        if (selectedSpecialty) {
            filtered = filtered.filter(doctor => 
            doctor.speciality === selectedSpecialty
            );
        }

        if (searchTerm) {
            filtered = filtered.filter(doctor =>
            doctor.user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            doctor.user.last_name.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        
        setFilteredDoctors(filtered);
    }, [doctors, searchTerm, selectedSpecialty]);

    const handleViewTimes = async (doctor) => {
        setSelectedDoctor(doctor);
        setAvailableSlots([]);
        setSlotsLoading(true);
        setShowSlotsModal(true);
        setError('');

        try {
            const response = await appointmentAPI.getAvailable({ 
                doctor_id: doctor.user.user_id 
            });
            const slotsData = Array.isArray(response.data) ? response.data : (response.data.results ? response.data.results : []);
            setAvailableSlots(slotsData);
        } catch (err) {
            setError('Failed to load available time slots.');
            setAvailableSlots([]);
        } finally {
            setSlotsLoading(false);
        }
    };

    const handleBookSlot = (slot) => {
        setSelectedSlot(slot);
        setShowSlotsModal(false);
        setShowBookingModal(true);
    };

    const handleConfirmBooking = async () => {
        if (!selectedSlot || !user) {
            setError('Missing booking information.');
            return;
        }

        setBookingLoading(true);
        setError('');

        try {
            const bookingData = {
                appointment: selectedSlot.appointment_id,
                reason: reason || 'Regular consultation'
            };
            
            console.log('🔍 Making booking request with data:', bookingData);
        
            const response = await appointmentAPI.createBooking(bookingData);
            
            console.log('✅ Booking response:', response.data);
            setSuccess(`Appointment booked successfully!`);
            setShowBookingModal(false);
            setSelectedSlot(null);
            setReason('');
            
            if (selectedDoctor) {
                handleViewTimes(selectedDoctor);
            }
            
        } catch (err) {
            const errorMsg = err.response?.data?.detail || err.response?.data?.appointment?.[0] || err.response?.data?.patient?.[0] || 'Failed to book appointment. Please try again.';
            setError(errorMsg);
        } finally {
            setBookingLoading(false);
        }
    };

    const groupSlotsByDay = (slots) => {
        if (!Array.isArray(slots)) {
            return {};
        }

        if (slots.length === 0) {
            return {};
        }

        const grouped = {};
        slots.forEach(slot => {
            const day = slot.week_day_display || slot.get_week_day_display || 'Unknown Day';
            if (!grouped[day]) {
                grouped[day] = [];
            }
            grouped[day].push(slot);
        });
        
        return grouped;
    };

    const formatTime = (timeString) => {
        return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    };

    return (
        <Container className="mt-4">
            <Row>
            <Col>
                <h2 className="mb-4">Book an Appointment</h2>
                
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
                        <Form.Label>Search Doctors</Form.Label>
                        <InputGroup>
                            <Form.Control
                            type="text"
                            placeholder="Search by doctor name..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </InputGroup>
                        </Form.Group>
                    </Col>
                    <Col md={6}>
                        <Form.Group className="mb-3">
                        <Form.Label>Filter by Specialty</Form.Label>
                        <Form.Select
                            value={selectedSpecialty}
                            onChange={(e) => setSelectedSpecialty(e.target.value)}
                        >
                            {specialties.map(specialty => (
                            <option key={specialty.value} value={specialty.value}>
                                {specialty.label}
                            </option>
                            ))}
                        </Form.Select>
                        </Form.Group>
                    </Col>
                    </Row>
                </Card.Body>
                </Card>

                {loading ? (
                <div className="text-center py-5">
                    <Spinner animation="border" role="status">
                    <span className="visually-hidden">Loading doctors...</span>
                    </Spinner>
                    <p className="mt-2">Loading available doctors...</p>
                </div>
                ) : (
                <Row>
                    {!Array.isArray(filteredDoctors) || filteredDoctors.length === 0 ? (
                    <Col>
                        <Alert variant="info">
                        {!Array.isArray(doctors) || doctors.length === 0 
                            ? 'No doctors available at the moment.' 
                            : 'No doctors found matching your search criteria.'
                        }
                        </Alert>
                    </Col>
                    ) : (
                    filteredDoctors.map(doctor => (
                        <Col md={6} lg={4} key={doctor.user.user_id} className="mb-4">
                        <Card className="h-100">
                            <Card.Body className="d-flex flex-column">
                            <div className="mb-3">
                                <h5 className="card-title mb-1">
                                Dr. {doctor.user.first_name} {doctor.user.last_name}
                                </h5>
                                <Badge bg="primary" className="mb-2">
                                {doctor.speciality}
                                </Badge>
                                <p className="text-muted small mb-2">
                                {doctor.experience} years of experience
                                </p>
                                {doctor.description && (
                                <p className="card-text small">
                                    {doctor.description.length > 100 
                                    ? `${doctor.description.substring(0, 100)}...` 
                                    : doctor.description
                                    }
                                </p>
                                )}
                            </div>
                            
                            <div className="mt-auto">
                                {doctor.working_days_display && (
                                <p className="text-muted small mb-2">
                                    <strong>Available:</strong> {doctor.working_days_display}
                                </p>
                                )}
                                {doctor.from_time && doctor.to_time && (
                                <p className="text-muted small mb-3">
                                    <strong>Hours:</strong> {formatTime(doctor.from_time)} - {formatTime(doctor.to_time)}
                                </p>
                                )}
                                
                                <Button 
                                variant="outline-primary" 
                                className="w-100"
                                onClick={() => handleViewTimes(doctor)}
                                disabled={!doctor.is_available}
                                >
                                {doctor.is_available ? 'View Available Times' : 'Not Available'}
                                </Button>
                            </div>
                            </Card.Body>
                        </Card>
                        </Col>
                    ))
                    )}
                </Row>
                )}
            </Col>
            </Row>

            <Modal 
            show={showSlotsModal} 
            onHide={() => setShowSlotsModal(false)}
            size="lg"
            >
            <Modal.Header closeButton>
                <Modal.Title>
                    Available Times - Dr. {selectedDoctor?.user.first_name} {selectedDoctor?.user.last_name}
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {slotsLoading ? (
                <div className="text-center py-4">
                    <Spinner animation="border" role="status">
                    <span className="visually-hidden">Loading time slots...</span>
                    </Spinner>
                    <p className="mt-2">Loading available time slots...</p>
                </div>
                ) : availableSlots.length === 0 ? (
                <Alert variant="info">
                    No available time slots for this doctor at the moment.
                </Alert>
                ) : (
                <div>
                    {Object.entries(groupSlotsByDay(availableSlots)).map(([day, slots]) => (
                    <div key={day} className="mb-4">
                        <h6 className="text-primary mb-3">{day}</h6>
                        <Row>
                        {slots.map(slot => (
                            <Col md={6} lg={4} key={slot.appointment_id} className="mb-2">
                            <Card className="time-slot-card">
                                <Card.Body className="p-3">
                                <div className="d-flex justify-content-between align-items-center">
                                    <div>
                                    <strong>{formatTime(slot.start_time)}</strong>
                                    {slot.end_time && (
                                        <span className="text-muted"> - {formatTime(slot.end_time)}</span>
                                    )}
                                    <br />
                                    <small className="text-muted">{slot.duration} minutes</small>
                                    </div>
                                    <Button 
                                    size="sm" 
                                    variant="success"
                                    onClick={() => handleBookSlot(slot)}
                                    >
                                    Book
                                    </Button>
                                </div>
                                </Card.Body>
                            </Card>
                            </Col>
                        ))}
                        </Row>
                    </div>
                    ))}
                </div>
                )}
            </Modal.Body>
            </Modal>

            <Modal 
            show={showBookingModal} 
            onHide={() => setShowBookingModal(false)}
            >
            <Modal.Header closeButton>
                <Modal.Title>Confirm Appointment Booking</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {selectedSlot && selectedDoctor && (
                <div>
                    <h6>Appointment Details:</h6>
                    <ul className="list-unstyled">
                    <li><strong>Doctor:</strong> Dr. {selectedDoctor.user.first_name} {selectedDoctor.user.last_name}</li>
                    <li><strong>Specialty:</strong> {selectedDoctor.speciality}</li>
                    <li><strong>Day:</strong> {selectedSlot.week_day_display}</li>
                    <li><strong>Time:</strong> {formatTime(selectedSlot.start_time)} - {formatTime(selectedSlot.end_time)}</li>
                    <li><strong>Duration:</strong> {selectedSlot.duration} minutes</li>
                    </ul>
                    
                    <Form.Group className="mt-3">
                    <Form.Label>Reason for Visit (Optional)</Form.Label>
                    <Form.Control
                        as="textarea"
                        rows={3}
                        placeholder="Describe the reason for your visit..."
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        maxLength={500}
                    />
                    <Form.Text className="text-muted">
                        {reason.length}/500 characters
                    </Form.Text>
                    </Form.Group>
                </div>
                )}
            </Modal.Body>
            <Modal.Footer>
                <Button 
                variant="secondary" 
                onClick={() => setShowBookingModal(false)}
                disabled={bookingLoading}
                >
                Cancel
                </Button>
                <Button 
                variant="primary" 
                onClick={handleConfirmBooking}
                disabled={bookingLoading}
                >
                {bookingLoading ? (
                    <>
                    <Spinner
                        as="span"
                        animation="border"
                        size="sm"
                        role="status"
                        className="me-2"
                    />
                    Booking...
                    </>
                ) : (
                    'Confirm Booking'
                )}
                </Button>
            </Modal.Footer>
            </Modal>
        </Container>
    );
};

export default AppointmentBrowser;