import api from './api';

export const getDoctors = async () => {
  const response = await api.get('/users/doctors/');
  return response.data;
};
