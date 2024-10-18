import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Token ee1bd22bd866a1d0e6e3db9ae3a1ef6094224e4b`  // TODO: replace with token from useAuth().userAuthentication.token
  },
  withCredentials: true,
});

// api.interceptors.request.use((config) => {
//   const { token } = useAuth().userAuthentication;
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// });

export default api;
