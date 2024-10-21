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
    profileImage: '', // Will store the image file 
  });

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [imageUploading, setImageUploading] = useState(false);  // State for tracking image upload
  const navigate = useNavigate(); 


  // Handle form field changes
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // Handle image upload as soon as the user selects the image
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    const username = formData.username;  // Get the username

    if (file && username) {
      setImageUploading(true);

      const formDataToUpload = new FormData();
      formDataToUpload.append('profile_image', file);

      try {
        // Upload image to the server
        const response = await fetch(`http://localhost:8000/authors/${username}/upload_image/`, {
          method: 'POST',
          body: formDataToUpload,
        });

        const result = await response.json();
        if (response.ok) {
          setFormData({
            ...formData,
            profileImage: result.url,  // Store the image URL in the form data
          });
        } else {
          setError(result.message || 'Image upload failed.');
        }
      } catch (err) {
        console.error('Image upload error:', err);
        setError('Image upload failed.');
      } finally {
        setImageUploading(false);
      }
    } else {
      setError('Please enter a username before uploading an image.');
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Submit the form data (with the uploaded profile image URL)
      const result = await signup(formData);
      console.log('Signup successful:', result);
      navigate('/');
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
          <label>Profile Image</label>
          <input
            type="file"
            name="profile_image"
            accept="image/*"
            onChange={handleImageUpload}  // Image is uploaded when selected
          />
          {imageUploading && <p>Uploading image...</p>}
          {formData.profileImage && <p>Image uploaded successfully.</p>}
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Signing Up...' : 'Sign Up'}
        </button>
      </form>
    </div>
  );
};

export default Signup;
