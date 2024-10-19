import api from './axios';

export const signup = async (signupData) => {
    try {
      const response = await api.post('/signup/', signupData, {
        headers: {
          'Content-Type': 'application/json', 
        },
      });
      return response.data;
    } catch (error) {
      console.error('Signup Error:', error.response?.data || error.message);
      throw error.response?.data || error; 
    }
  };