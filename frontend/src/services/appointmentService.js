import api from './api';

// Get all appointments for the current user
export const getUserAppointments = async () => {
  const response = await api.get('/appointments/user/');
  return response.data;
};

// Get available time slots for a specific doctor on a specific date
export const getDoctorAvailability = async (doctorId, date) => {
  const response = await api.get(`/appointments/availability/${doctorId}/`, {
    params: { date }
  });
  return response.data;
};

// Book a new appointment
export const bookAppointment = async (appointmentData) => {
  const response = await api.post('/appointments/', appointmentData);
  return response.data;
};

// Cancel an appointment
export const cancelAppointment = async (appointmentId) => {
  const response = await api.delete(`/appointments/${appointmentId}/`);
  return response.data;
};

// Reschedule an appointment
export const rescheduleAppointment = async (appointmentId, newData) => {
  const response = await api.patch(`/appointments/${appointmentId}/`, newData);
  return response.data;
};

// Get appointment details
export const getAppointmentDetails = async (appointmentId) => {
  const response = await api.get(`/appointments/${appointmentId}/`);
  return response.data;
};