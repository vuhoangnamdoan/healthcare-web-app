import React, { useState, useEffect} from 'react';
import { 
    Container, Card, Table, Alert, Spinner, Button, Row, Col, Badge, Modal, Form
} from 'react-bootstrap';
import { doctorAPI, authAPI } from '../../services/api';


const AppointmentSlots = () => {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [creating, setCreating] = useState(false);
    const [createSuccess, setCreateSuccess] = useState('');
    const [doctorProfile, setDoctorProfile] = useState(null);

    const [newAppointment, setNewAppointment] = useState({
        week_day: '',
        start_time: '',
        duration: 60
    });

    const allDayOptions = [
        { value: '1', label: 'Monday' },
        { value: '2', label: 'Tuesday' },
        { value: '3', label: 'Wednesday' },
        { value: '4', label: 'Thursday' },
        { value: '5', label: 'Friday' },
        { value: '6', label: 'Saturday' },
        { value: '7', label: 'Sunday' },
    ];

    // Get filtered day options based on doctor's working days
    const getAvailableDayOptions = () => {
        if (!doctorProfile?.working_day) {
            return allDayOptions;
        }

        try {
            const workingDays = doctorProfile.working_day.split(',').map(day => parseInt(day.trim())).filter(day => !isNaN(day));
            // Filter day options to only include working days
            return allDayOptions.filter(option => workingDays.includes(parseInt(option.value)));
        } catch (error) {
            console.error('Error parsing working days:', error);
            return allDayOptions;
        }
    };

    useEffect(() => {
        fetchDoctorProfile();
        fetchMyAppointments();
    }, []);

    const fetchDoctorProfile = async () => {
        try {
            const response = await authAPI.getProfile();
            setDoctorProfile(response.data);
        } catch (err) {
            console.error('Failed to fetch doctor profile:', err);
        }
    };

    const fetchMyAppointments = async () => {
        setLoading(true);
        setError('');
        
        try {
            const response = await doctorAPI.getMyAppointments();
            const appointmentsData = Array.isArray(response.data) ? response.data : (response.data.results ? response.data.results : []);
            
            appointmentsData.sort((a, b) => {
                if (a.week_day !== b.week_day) {
                    return (a.week_day || 0) - (b.week_day || 0);
                }
                return (a.start_time || '').localeCompare(b.start_time || '');
            });
            
            setAppointments(appointmentsData);
            
        } catch (err) {
            setError('Failed to fetch appointment slots. Please try again.');
            setAppointments([]);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateAppointment = async (e) => {
        e.preventDefault();
        setCreating(true);
        setError('');
        setCreateSuccess('');

        try {
            if (!newAppointment.week_day || !newAppointment.start_time) {
                throw new Error('Please fill in all required fields.');
            }

            // Validate time is within working hours
            if (doctorProfile?.from_time && doctorProfile?.to_time) {
                const selectedTime = newAppointment.start_time;
                if (selectedTime < doctorProfile.from_time || selectedTime >= doctorProfile.to_time) {
                    throw new Error(`Appointment time must be between ${doctorProfile.from_time} and ${doctorProfile.to_time}.`);
                }
            }
            await doctorAPI.createAppointmentSlot(newAppointment);
            setCreateSuccess('Appointment slot created successfully!');
            setNewAppointment({week_day: '', start_time: '', duration: 60});
            
            setTimeout(() => {
                setShowCreateModal(false);
                setCreateSuccess('');
                fetchMyAppointments();
            }, 1500);
            
        } catch (err) {
            setError(err.message || 'Failed to create appointment slot. Please try again.');
        } finally {
            setCreating(false);
        }
    };

    const handleModalClose = () => {
        setShowCreateModal(false);
        setError('');
        setCreateSuccess('');
        setNewAppointment({week_day: '', start_time: '', duration: 60});
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewAppointment(prev => ({...prev, [name]: value}));
    };

    const formatTime = (timeString) => {
        if (!timeString) return 'N/A';
        try {
            const time = timeString.includes(':') ? timeString : `${timeString}:00`;
            return new Date(`2000-01-01T${time}`).toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit', hour12: true});
        } catch (error) {
            return timeString;
        }
    };

    const getStatusBadge = (appointment) => {
        const status = appointment.slot_status || 
        (appointment.bookings && appointment.bookings.some(b => !b.is_canceled) ? 'Booked' : 'Available');
        
        return status === 'Available' ? 
        <Badge bg="success">Available</Badge> : <Badge bg="danger">Booked</Badge>;
    };

    const getDayName = (appointment) => {
        return appointment.week_day_display || `Day ${appointment.week_day}` || 'Unknown Day';
    };

    const formatCreatedDate = (dateString) => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleDateString('en-US', {month: 'short', day: 'numeric', year: 'numeric'});
        } catch (error) {
            return 'Invalid Date';
        }
    };

    const handleRefresh = () => {
        setError('');
        fetchMyAppointments();
    };

    if (loading) {
        return (
            <Container className="d-flex justify-content-center align-items-center" style={{ height: '50vh' }}>
                <div className="text-center">
                <Spinner animation="border" role="status" variant="primary">
                    <span className="visually-hidden">Loading...</span>
                </Spinner>
                <p className="mt-3 text-muted">Loading your appointment slots...</p>
                </div>
            </Container>
        );
    }

    const availableDayOptions = getAvailableDayOptions();

    return (
        <Container className="mt-4">
        <Row className="mb-4">
            <Col>
            <div className="d-flex justify-content-between align-items-center">
                <div>
                <h2 className="mb-1">My Appointment Slots</h2>
                <p className="text-muted mb-0">
                    Manage your available appointment time slots for patients to book.
                </p>
                {doctorProfile?.working_day && (
                    <small className="text-info">
                    Working Days: {getAvailableDayOptions().map(opt => opt.label).join(', ')}
                    {
                        doctorProfile.from_time && 
                        doctorProfile.to_time && 
                        ` | Hours: ${formatTime(doctorProfile.from_time)} - ${formatTime(doctorProfile.to_time)}`
                    }
                    </small>
                )}
                </div>
                <div>
                <Button 
                    variant="primary" 
                    onClick={() => setShowCreateModal(true)}
                    className="me-2"
                    disabled={availableDayOptions.length === 0}
                >
                    Create New Slot
                </Button>
                <Button 
                    variant="outline-primary" 
                    onClick={handleRefresh}
                    disabled={loading}
                >
                    Refresh
                </Button>
                </div>
            </div>
            </Col>
        </Row>

        {availableDayOptions.length === 0 && (
            <Alert variant="warning">
                <strong>No working days configured!</strong> Please update your profile to set your working days before creating appointment slots.
            </Alert>
        )}

        {error && (
            <Alert variant="danger" dismissible onClose={() => setError('')}>
                <strong>Error:</strong> {error}
            </Alert>
        )}

        <Card>
            <Card.Header>
            <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">All My Appointment Slots</h5>
                <Badge bg="info" pill>
                    {appointments.length} {appointments.length === 1 ? 'slot' : 'slots'}
                </Badge>
            </div>
            </Card.Header>
            
            <Card.Body>
            {appointments.length === 0 ? (
                <div className="text-center py-5">
                    <div className="mb-3">
                        <span style={{ fontSize: '3rem' }}>📅</span>
                    </div>
                    <h5 className="text-muted">No appointment slots found</h5>
                    <p className="text-muted mb-4">
                        Create your first appointment slot to allow patients to book appointments with you.
                    </p>
                    <Button 
                        variant="primary" 
                        onClick={() => setShowCreateModal(true)}
                        disabled={availableDayOptions.length === 0}
                    >
                        Create Your First Slot
                    </Button>
                </div>
            ) : (
                <>
                <div className="table-responsive">
                    <Table hover>
                    <thead className="table-light">
                        <tr>
                        <th>Day</th>
                        <th>Time Slot</th>
                        <th>Duration</th>
                        <th>Status</th>
                        <th>Created Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {appointments.map((appointment, index) => (
                        <tr key={appointment.appointment_id || `appointment-${index}`}>
                            <td>
                                <strong>{getDayName(appointment)}</strong>
                            </td>
                            <td>
                                <span className="text-primary">
                                    {formatTime(appointment.start_time)}
                                </span>
                                {' - '}
                                <span className="text-primary">
                                    {formatTime(appointment.end_time)}
                                </span>
                            </td>
                            <td>
                                {appointment.duration || 60} minutes
                            </td>
                            <td>
                                {getStatusBadge(appointment)}
                            </td>
                            <td>
                                <small className="text-muted">
                                    {formatCreatedDate(appointment.created_at)}
                                </small>
                            </td>
                        </tr>
                        ))}
                    </tbody>
                    </Table>
                </div>
                
                <div className="mt-3 p-3 bg-light rounded">
                    <small className="text-muted">
                        💡 <strong>Tip:</strong> Patients can book your available slots through the appointment browser. Booked slots will show as "Booked" status.
                    </small>
                </div>
                </>
            )}
            </Card.Body>
        </Card>

        <Modal show={showCreateModal} onHide={handleModalClose} centered>
            <Modal.Header closeButton>
                <Modal.Title>Create New Appointment Slot</Modal.Title>
            </Modal.Header>
            <Modal.Body>
            {createSuccess && (
                <Alert variant="success">
                    {createSuccess}
                </Alert>
            )}
            
            {error && (
                <Alert variant="danger">
                <strong>Error:</strong> {error}
                </Alert>
            )}

            {availableDayOptions.length === 0 ? (
                <Alert variant="warning">
                    <strong>No working days configured!</strong><br />
                    Please update your profile to set your working days before creating appointment slots.
                </Alert>
            ) : (
                <Form onSubmit={handleCreateAppointment}>
                <Form.Group className="mb-3">
                    <Form.Label>Day of Week <span className="text-danger">*</span></Form.Label>
                    <Form.Select
                    name="week_day"
                    value={newAppointment.week_day}
                    onChange={handleInputChange}
                    required
                    >
                        <option value="">Select a day</option>
                        {availableDayOptions.map(day => (
                            <option key={day.value} value={day.value}>
                            {day.label}
                            </option>
                        ))}
                    </Form.Select>
                    <Form.Text className="text-muted">
                        Only showing your working days: {availableDayOptions.map(opt => opt.label).join(', ')}
                    </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                    <Form.Label>Start Time <span className="text-danger">*</span></Form.Label>
                    <Form.Control
                    type="time"
                    name="start_time"
                    value={newAppointment.start_time}
                    onChange={handleInputChange}
                    min={doctorProfile?.from_time}
                    max={doctorProfile?.to_time}
                    required
                    />
                    <Form.Text className="text-muted">
                        {doctorProfile?.from_time && doctorProfile?.to_time 
                            ? `Working hours: ${formatTime(doctorProfile.from_time)} - ${formatTime(doctorProfile.to_time)}`
                            : 'Select the start time for this appointment slot'
                        }
                    </Form.Text>
                </Form.Group>

                <Form.Group className="mb-3">
                    <Form.Label>Duration (minutes)</Form.Label>
                    <Form.Select
                        name="duration"
                        value={newAppointment.duration}
                        onChange={handleInputChange}
                        >
                        <option value={30}>30 minutes</option>
                        <option value={45}>45 minutes</option>
                        <option value={60}>60 minutes</option>
                        <option value={90}>90 minutes</option>
                        <option value={120}>120 minutes</option>
                    </Form.Select>
                </Form.Group>

                <div className="d-flex justify-content-end">
                    <Button 
                        variant="secondary" 
                        onClick={handleModalClose}
                        className="me-2"
                        disabled={creating}
                        >
                        Cancel
                    </Button>
                    <Button 
                    variant="primary" 
                    type="submit"
                    disabled={creating}
                    >
                        {creating ? (
                            <>
                            <Spinner size="sm" className="me-2" />
                            Creating...
                            </>
                        ) : (
                            'Create Slot'
                        )}
                    </Button>
                </div>
                </Form>
            )}
            </Modal.Body>
        </Modal>
        </Container>
    );
};

export default AppointmentSlots;