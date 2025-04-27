import React, { useState, useEffect } from 'react';
import { Container, Card, Alert, Spinner, Button } from 'react-bootstrap';
import { Calendar, momentLocalizer } from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import { getUserAppointments } from '../services/appointmentService';

// Set up the localizer for react-big-calendar
const localizer = momentLocalizer(moment);

const AppointmentCalendar = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        setLoading(true);
        const data = await getUserAppointments();
        
        // Transform appointments for calendar display
        const calendarEvents = data.map(appointment => ({
          id: appointment.id,
          title: `Dr. ${appointment.doctor_name} - ${appointment.reason || 'Appointment'}`,
          start: new Date(appointment.appointment_datetime),
          end: moment(appointment.appointment_datetime)
            .add(30, 'minutes')
            .toDate(),
          appointment: appointment,
          status: appointment.status
        }));
        
        setAppointments(calendarEvents);
      } catch (err) {
        console.error('Error fetching appointments:', err);
        setError('Failed to load your appointments. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  // Handle event click to see appointment details
  const handleEventClick = (event) => {
    navigate(`/appointments/${event.id}`);
  };

  // Custom event styling based on appointment status
  const eventStyleGetter = (event) => {
    let backgroundColor;
    switch (event.status) {
      case 'SCHEDULED':
        backgroundColor = '#0d6efd'; // blue
        break;
      case 'COMPLETED':
        backgroundColor = '#198754'; // green
        break;
      case 'CANCELLED':
        backgroundColor = '#dc3545'; // red
        break;
      case 'MISSED':
        backgroundColor = '#6c757d'; // gray
        break;
      default:
        backgroundColor = '#0d6efd';
    }

    return {
      style: {
        backgroundColor,
        borderRadius: '5px',
        opacity: 0.8,
        color: 'white',
        border: '0px',
        display: 'block',
        cursor: 'pointer'
      }
    };
  };

  // Custom toolbar with additional navigation options
  const CustomToolbar = ({ label, onNavigate, onView }) => {
    return (
      <div className="rbc-toolbar">
        <span className="rbc-btn-group">
          <Button variant="outline-primary" onClick={() => onNavigate('PREV')}>
            Back
          </Button>
          <Button variant="outline-primary" onClick={() => onNavigate('TODAY')}>
            Today
          </Button>
          <Button variant="outline-primary" onClick={() => onNavigate('NEXT')}>
            Next
          </Button>
        </span>
        <span className="rbc-toolbar-label">{label}</span>
        <span className="rbc-btn-group">
          <Button variant="outline-primary" onClick={() => onView('month')}>
            Month
          </Button>
          <Button variant="outline-primary" onClick={() => onView('week')}>
            Week
          </Button>
          <Button variant="outline-primary" onClick={() => onView('day')}>
            Day
          </Button>
          <Button variant="outline-primary" onClick={() => onView('agenda')}>
            Agenda
          </Button>
        </span>
      </div>
    );
  };

  return (
    <Layout>
      <Container className="mt-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>Appointment Calendar</h2>
          <Button 
            variant="success" 
            onClick={() => navigate('/appointments/book')}
          >
            Book New Appointment
          </Button>
        </div>
        
        {error && <Alert variant="danger">{error}</Alert>}
        
        <Card className="mb-4">
          <Card.Body>
            {loading ? (
              <div className="text-center py-5">
                <Spinner animation="border" />
                <p className="mt-2">Loading your appointments...</p>
              </div>
            ) : appointments.length === 0 ? (
              <Alert variant="info">
                You don't have any appointments scheduled. 
                <Button 
                  variant="link" 
                  onClick={() => navigate('/appointments/book')}
                  className="p-0 ms-2"
                >
                  Book your first appointment
                </Button>
              </Alert>
            ) : (
              <div style={{ height: '700px' }}>
                <Calendar
                  localizer={localizer}
                  events={appointments}
                  startAccessor="start"
                  endAccessor="end"
                  style={{ height: '100%' }}
                  onSelectEvent={handleEventClick}
                  eventPropGetter={eventStyleGetter}
                  components={{
                    toolbar: CustomToolbar
                  }}
                  views={['month', 'week', 'day', 'agenda']}
                  popup
                />
              </div>
            )}
          </Card.Body>
        </Card>
      </Container>
    </Layout>
  );
};

export default AppointmentCalendar;