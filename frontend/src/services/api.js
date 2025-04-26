import axios from 'axios';

// Create axios instance with base URL
const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
});

// Add request interceptor for authentication
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// API services for appointments
export const appointmentService = {
  getAll: () => API.get('/appointments/'),
  getById: (id) => API.get(`/appointments/${id}/`),
  create: (data) => API.post('/appointments/', data),
  update: (id, data) => API.put(`/appointments/${id}/`, data),
  delete: (id) => API.delete(`/appointments/${id}/`),
};

// API services for users
export const userService = {
  login: (credentials) => API.post('/users/login/', credentials),
  register: (userData) => API.post('/users/register/', userData),
  getCurrentUser: () => API.get('/users/me/'),
};

// API services for notifications
export const notificationService = {
  getAll: () => API.get('/notifications/'),
  markAsRead: (id) => API.put(`/notifications/${id}/read/`),
};

export default API;
