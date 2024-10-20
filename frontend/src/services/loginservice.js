import axios from 'axios';
import api from './axios';

export const login = async (loginData) => {
  try {
    const response = await api.post('users/login/', loginData);
    // console.log(response);
    return response.data;
  } catch (error) {
    throw error;
  }
};
