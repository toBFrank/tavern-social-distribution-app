import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';  // Use useNavigate instead of useHistory
import { getAuthorProfile, updateAuthorProfile } from '../services/editProfileService'; 
import '../styles/pages/EditProfile.css';  // Import CSS for styling

const EditProfile = () => {
    const { authorId } = useParams();  // Get authorId from URL parameters
    const navigate = useNavigate();  // Use useNavigate for navigation
    const [profileData, setProfileData] = useState({ displayName: '', github: '', profileImage: '' });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Fetch profile data when the component mounts
        getAuthorProfile(authorId)
            .then(data => {
                setProfileData({
                    displayName: data.displayName,
                    github: data.github,
                    profileImage: data.profileImage,
                });
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setError('Error loading profile data.');
                setLoading(false);
            });
    }, [authorId]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setProfileData((prevData) => ({
            ...prevData,
            [name]: value,
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        updateAuthorProfile(authorId, profileData)  // Update profile using the service
            .then(() => {
                navigate(`/authors/${authorId}/profile`);  // Redirect to the profile page after updating
            })
            .catch(err => {
                console.error(err);
                setError('Error updating profile.');
            });
    };

    // Show loading message or an error message if data is not available
    if (loading) {
        return <p>Loading...</p>;
    }

    return (
        <div className="edit-profile-page">
            <h1>Edit Profile</h1>
            {error && <p className="error">{error}</p>}
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="displayName">Display Name</label>
                    <input
                        type="text"
                        id="displayName"
                        name="displayName"
                        value={profileData.displayName}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="github">GitHub Profile</label>
                    <input
                        type="url"
                        id="github"
                        name="github"
                        value={profileData.github}
                        onChange={handleChange}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="profileImage">Profile Image URL</label>
                    <input
                        type="url"
                        id="profileImage"
                        name="profileImage"
                        value={profileData.profileImage}
                        onChange={handleChange}
                        required
                    />
                </div>
                <button type="submit">Save Changes</button>
            </form>
        </div>
    );
};

export default EditProfile;
