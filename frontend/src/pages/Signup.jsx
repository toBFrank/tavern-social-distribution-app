import React, { useState } from 'react';
import { signup } from '../services/signupservice'; 
import { useNavigate } from 'react-router-dom'; 

const Signup = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '', 
    password: '',
    displayName: '', 
    github: '', 
    profileImage: '', 
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
      
      const result = await signup(formData);
      console.log('Signup successful:', result);

      
      navigate('/home');
    } catch (err) {
      console.error('Signup failed:', err);
      setError(err.message || 'Signup failed. Please try again.');
    } finally {
      setLoading(false); 
    }
  };

  return (
    <div className="signup-container">
      <h2>Sign Up</h2>

      {/* Show error message if there is one */}
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
          <label>Email</label> 
          <input
            type="email" 
            name="email" 
            value={formData.email} 
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

        <div className="form-group">
          <label>Name</label>
          <input
            type="text"
            name="displayName"
            value={formData.displayName}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label>GitHub</label>
          <input
            type="text"
            name="github"
            value={formData.github}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label>Profile Image URL</label>
          <input
            type="url"
            name="profileImage"
            value={formData.profileImage}
            onChange={handleChange}
          />
        </div>

        {/* Submit button is disabled when loading */}
        <button type="submit" disabled={loading}>
          {loading ? 'Signing Up...' : 'Sign Up'}
        </button>
      </form>
    </div>
  );
};

export default Signup;
