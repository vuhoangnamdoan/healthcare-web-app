import axios from 'axios';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api'  // ← Production: uses relative URLs with Kubernetes Ingress
  : 'http://localhost:8000/api';  // ← Development: uses full URL

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken
          });
          
          const { access } = response.data;
          localStorage.setItem('accessToken', access);
          
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          window.location.href = '/auth/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API endpoints
export const authAPI = {
  login: (credentials) => apiClient.post('/auth/token/', credentials),
  register: (userData) => apiClient.post('/users/register/', userData),
  getProfile: () => apiClient.get('/users/profile/'),
  updateProfile: (data) => apiClient.put('/users/profile/update/', data),
  changePassword: (data) => apiClient.post('/users/change-password/', data),
  refreshToken: (refresh) => apiClient.post('/auth/token/refresh/', { refresh }),
};

// Appointment API endpoints
export const appointmentAPI = {
  getAvailable: (params) => apiClient.get('/appointments/available/', { params }),
  getMyBookings: () => apiClient.get('/appointments/my-bookings/'),
  createBooking: (data) => apiClient.post('/appointments/bookings/', data),
  cancelBooking: (id, data) => apiClient.post(`/appointments/bookings/${id}/cancel/`, data),
  getBookingDetail: (id) => apiClient.get(`/appointments/bookings/${id}/`),
};

export const doctorAPI = {
  getMyAppointments: () => apiClient.get('/appointments/my-appointments/'),
  createAppointmentSlot: (data) => apiClient.post('/appointments/availability/', data),
  updateAppointmentSlot: (id, data) => apiClient.put(`/appointments/slots/${id}/`, data),
  deleteAppointmentSlot: (id) => apiClient.delete(`/appointments/slots/${id}/`),
  getPatientBookings: () => apiClient.get('/appointments/my-bookings/'),
};
 
// User API endpoints
export const userAPI = {
  getDoctors: (params) => apiClient.get('/users/doctors/', { params }),
  getDoctor: (id) => apiClient.get(`/users/doctors/${id}/`),
  getPatients: (params) => apiClient.get('/users/patients/', { params }),
  getPatient: (id) => apiClient.get(`/users/patients/${id}/`),
};

export default apiClient;