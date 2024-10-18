import api from './axios';

export const login = async (loginData) => {
    try {
      const response = await api.post('/login/', loginData, {
        headers: {
          'Content-Type': 'application/json', 
        },
      });
      console.log(response.data);
      return response.data;
    } catch (error) {
      console.error('Signup Error:', error.response?.data || error.message);
      throw error.response?.data || error; 
    }
  };