import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import Layout from '../components/layout/Layout';
import { getDoctorAvailability, bookAppointment } from '../services/appointmentService';
import { getDoctors } from '../services/doctorService';

const AppointmentBooking = () => {
  const { doctorId } = useParams();
  const navigate = useNavigate();
  
  const [doctors, setDoctors] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState(doctorId || '');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState('');
  const [reason, setReason] = useState('');
  const [notes, setNotes] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [slotLoading, setSlotLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Fetch doctors list
  useEffect(() => {
    const fetchDoctors = async () => {
      try {
        const data = await getDoctors();
        setDoctors(data);
        
        // If doctorId is provided but no doctor is selected, set it
        if (doctorId && !selectedDoctor) {
          setSelectedDoctor(doctorId);
        }
      } catch (err) {
        console.error('Error fetching doctors:', err);
        setError('Failed to load doctors. Please try again later.');
      }
    };

    fetchDoctors();
  }, [doctorId, selectedDoctor]);

  // Fetch available slots when doctor or date changes
  useEffect(() => {
    const fetchAvailability = async () => {
      if (!selectedDoctor) return;
      
      try {
        setSlotLoading(true);
        setError('');
        
        // Format date as YYYY-MM-DD for API
        const formattedDate = selectedDate.toISOString().split('T')[0];
        
        const data = await getDoctorAvailability(selectedDoctor, formattedDate);
        setAvailableSlots(data.available_slots || []);
        setSelectedSlot(''); // Reset selected slot when date/doctor changes
      } catch (err) {
        console.error('Error fetching availability:', err);
        setError('Failed to load available time slots.');
        setAvailableSlots([]);
      } finally {
        setSlotLoading(false);
      }
    };

    fetchAvailability();
  }, [selectedDoctor, selectedDate]);

  const handleDateChange = (date) => {
    setSelectedDate(date);
  };

  const handleDoctorChange = (e) => {
    setSelectedDoctor(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedDoctor || !selectedSlot) {
      setError('Please select a doctor and an available time slot.');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      const appointmentData = {
        doctor: selectedDoctor,
        appointment_datetime: selectedSlot,
        reason: reason,
        notes: notes
      };
      
      await bookAppointment(appointmentData);
      setSuccess('Appointment booked successfully!');
      
      // Reset form
      setSelectedSlot('');
      setReason('');
      setNotes('');
      
      // Redirect to appointments list after a short delay
      setTimeout(() => {
        navigate('/appointments');
      }, 2000);
    } catch (err) {
      console.error('Error booking appointment:', err);
      setError('Failed to book appointment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Find the current doctor's name if selected
  const currentDoctor = doctors.find(doc => doc.id.toString() === selectedDoctor?.toString());
  const doctorName = currentDoctor 
    ? `${currentDoctor.first_name} ${currentDoctor.last_name}` 
    : '';

  return (
    <Layout>
      <Container className="mt-4">
        <h2 className="mb-4">Book an Appointment</h2>
        
        {error && <Alert variant="danger">{error}</Alert>}
        {success && <Alert variant="success">{success}</Alert>}
        
        <Card>
          <Card.Body>
            <Form onSubmit={handleSubmit}>
              <Row className="mb-3">
                <Form.Group as={Col} md={6}>
                  <Form.Label>Select Doctor</Form.Label>
                  <Form.Select
                    value={selectedDoctor}
                    onChange={handleDoctorChange}
                    disabled={loading || !!doctorId}
                    required
                  >
                    <option value="">-- Select a doctor --</option>
                    {doctors.map((doctor) => (
                      <option key={doctor.id} value={doctor.id}>
                        Dr. {doctor.first_name} {doctor.last_name} 
                        {doctor.doctor_profile?.specialization 
                          ? ` - ${doctor.doctor_profile.specialization}` 
                          : ''}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
                
                <Form.Group as={Col} md={6}>
                  <Form.Label>Select Date</Form.Label>
                  <div>
                    <DatePicker
                      selected={selectedDate}
                      onChange={handleDateChange}
                      minDate={new Date()}
                      className="form-control"
                      dateFormat="MMMM d, yyyy"
                      disabled={loading}
                      required
                    />
                  </div>
                </Form.Group>
              </Row>
              
              <Form.Group className="mb-3">
                <Form.Label>Available Time Slots</Form.Label>
                {slotLoading ? (
                  <div className="text-center py-3">
                    <Spinner animation="border" size="sm" />
                    <span className="ms-2">Loading available slots...</span>
                  </div>
                ) : availableSlots.length === 0 ? (
                  <Alert variant="info">
                    No available slots for {doctorName} on {selectedDate.toLocaleDateString()}. 
                    Please select a different date.
                  </Alert>
                ) : (
                  <div className="d-flex flex-wrap gap-2 mb-3">
                    {availableSlots.map((slot) => (
                      <Button
                        key={slot}
                        variant={selectedSlot === slot ? "primary" : "outline-primary"}
                        onClick={() => setSelectedSlot(slot)}
                        className="time-slot-btn"
                      >
                        {new Date(slot).toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </Button>
                    ))}
                  </div>
                )}
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Reason for Appointment</Form.Label>
                <Form.Control
                  as="select"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  disabled={loading}
                  required
                >
                  <option value="">-- Select a reason --</option>
                  <option value="Consultation">Consultation</option>
                  <option value="Follow-up">Follow-up</option>
                  <option value="Checkup">Routine Checkup</option>
                  <option value="Emergency">Emergency</option>
                  <option value="Prescription">Prescription Refill</option>
                  <option value="Other">Other</option>
                </Form.Control>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Additional Notes (Optional)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Enter any additional details or symptoms"
                  disabled={loading}
                />
              </Form.Group>
              
              <div className="d-grid gap-2">
                <Button 
                  type="submit" 
                  variant="success"
                  disabled={!selectedDoctor || !selectedSlot || loading}
                >
                  {loading ? (
                    <>
                      <Spinner animation="border" size="sm" className="me-2" />
                      Booking Appointment...
                    </>
                  ) : (
                    'Book Appointment'
                  )}
                </Button>
                <Button 
                  type="button" 
                  variant="outline-secondary"
                  onClick={() => navigate('/doctors')}
                  disabled={loading}
                >
                  Cancel
                </Button>
              </div>
            </Form>
          </Card.Body>
        </Card>
      </Container>
    </Layout>
  );
};

export default AppointmentBooking;