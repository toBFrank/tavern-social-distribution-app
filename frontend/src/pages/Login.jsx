import React, { useState } from 'react';
import { login } from '../services/loginservice'; 
import { useNavigate } from 'react-router-dom'; 


const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });


  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); 

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value, 
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); 
    setLoading(true);
    setError('');

    try {
      const result = await login(formData);
      console.log('Login successful:', result);
      // Store tokens securely
      if (result?.access && result?.author.id) {

        localStorage.setItem('accessToken', result.access);
        localStorage.setItem('authorId', result.author.id);
      }

      navigate('/home');
    } catch (err) {
      console.error('Login failed:', err);
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false); 
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Logging In...' : 'Log In'}
        </button>
      </form>
    </div>
  );
};

export default Login;
