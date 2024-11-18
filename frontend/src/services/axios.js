import axios from 'axios';
import Cookies from 'js-cookie';

const api = axios.create({
  baseURL: `localhost:8000/api/`,
  withCredentials: true,
});

api.interceptors.request.use(
  (config) => {
    const accessToken = Cookies.get('access_token');

    if (config.data instanceof FormData) {
      // config.headers['Content-Type'] = 'multipart/form-data';
    } else {
      config.headers['Content-Type'] = 'application/json';
    }

    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`;
    } else {
      delete config.headers['Authorization'];
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Refresh access token if expired
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = Cookies.get('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(
            `${window.location.origin}/api/users/token/refresh/`,
            {
              refresh: refreshToken,
            }
          );
          const accessToken = response.data['access'];
          
          Cookies.set('access_token', accessToken, { sameSite: 'strict' });
          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
          return axios(originalRequest);
        } catch (refreshError) {
          Cookies.remove('access_token');
          Cookies.remove('refresh_token');
          Cookies.remove('author_id');
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
