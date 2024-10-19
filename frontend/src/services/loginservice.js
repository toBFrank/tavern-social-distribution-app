import axios from 'axios';

export const login = async (loginData) => {
  try {
    // const response = await api.post('users/login/', loginData);
    const response = axios.post(
      'http://localhost:8000/api/users/login/',
      loginData
    );
    return response.data;
  } catch (error) {
    console.log(error);
    throw error;
  }
};
