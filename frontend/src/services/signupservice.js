import api from './axios';  // Adjust the path based on your project structure

export const signup = async (signupData) => {
  try {
    const response = await api.post('http://localhost:8000/signup/', signupData, {
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });
    if (response.status === 201) {
      // Redirect user to login after successful signup
      window.location.href = '/login';
    }
  } catch (error) {
    console.error('Signup Error:', error.response?.data || error.message);
  }
};
