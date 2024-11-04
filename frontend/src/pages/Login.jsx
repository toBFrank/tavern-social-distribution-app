import React, { useState } from 'react';
import Cookies from 'js-cookie';
import '../styles/pages/Login.css';
import { login } from '../services/loginservice';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  //#region Properties
  const [loading, setLoading] = useState(false);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const navigate = useNavigate();
  //#endregion

  //#region Event Handlers
  const handleSubmit = async (e) => {
    e.preventDefault();
    const loginData = {
      username: username,
      password: password,
    };

    try {
      setLoading(true);
      const response = await login(loginData);
      if (!response) {
        throw new Error('Login failed: No response');
      }
      const { refresh_token, access_token, author_id } = response;

      Cookies.set('author_id', author_id); 
      Cookies.set('access_token', access_token);
      Cookies.set('refresh_token', refresh_token);

      setLoading(false);
      navigate('/');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };
  //#endregion

  return (
    <div className="login-background-container">
      <h1 className="login-pg-title">Tavern</h1>
      <div className="login-container">
        <h1 className="login-title">Log In</h1>
        <form className="form-container" onSubmit={handleSubmit} method="post">
          <div className="form-group">
            <label className="input-label">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="input-label">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          
          <button className="login-button" type="submit" disabled={loading}>
            Log In
          </button>
        </form>
        <div className="signup-link">
          No account? <span onClick={() => navigate('/signup')}>Sign Up</span>
        </div>
      </div>
    </div>
  );
};

export default Login;
