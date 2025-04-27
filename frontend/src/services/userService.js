import api from './api';

// User authentication and profile services
export const loginUser = async (email, password) => {
  const response = await api.post('/users/login/', { email, password });
  return response.data;
};

export const registerUser = async (userData) => {
  const response = await api.post('/users/register/', userData);
  return response.data;
};

export const fetchUserProfile = async () => {
  const response = await api.get('/users/profile/');
  return response.data;
};

export const updateUserProfile = async (profileData) => {
  const response = await api.put('/users/profile/', profileData);
  return response.data;
};
