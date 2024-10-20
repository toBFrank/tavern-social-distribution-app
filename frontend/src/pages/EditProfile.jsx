import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getAuthorProfile, updateAuthorProfile } from '../services/editProfileService';
import '../styles/pages/EditProfile.css';

const EditProfile = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        displayName: '',
        github: '',
        profileImage: ''
    });
    const [loading, setLoading] = useState(true);
    const [errors, setErrors] = useState({});

    // Fetch author details when the component mounts
    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const data = await getAuthorProfile(id);
                setFormData({
                    displayName: data.displayName,
                    github: data.github,
                    profileImage: data.profileImage
                });
                setLoading(false);
            } catch (error) {
                console.error('Error fetching profile:', error);
            }
        };

        fetchProfile();
    }, [id]);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Transform formData to match the field names expected by the backend
        const updatedData = {
            display_name: formData.displayName,  // Transform displayName to display_name
            github: formData.github,
            profile_image: formData.profileImage  // Transform profileImage to profile_image
        };

        try {
            await updateAuthorProfile(id, updatedData);  // Send the transformed data
            navigate(`/profile/${id}`);
        } catch (error) {
            console.error('Error updating profile:', error);
            setErrors({ general: 'Failed to update profile' });
        }
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <div className="edit-profile-page">
            <div className="edit-profile-container">
                <h1>Edit Profile</h1>

                {/* Profile Image Preview */}
                {formData.profileImage && (
                    <div className="profile-image-preview">
                        <img src={formData.profileImage} alt="Current Profile" />
                    </div>
                )}

                <form onSubmit={handleSubmit} className="edit-profile-form">
                    <div className="form-group">
                        <label htmlFor="displayName">Display Name:</label>
                        <input
                            type="text"
                            id="displayName"
                            name="displayName"
                            placeholder="Enter display name"
                            value={formData.displayName}
                            onChange={handleChange}
                        />
                        {errors.displayName && <p className="error">{errors.displayName}</p>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="github">GitHub:</label>
                        <input
                            type="url"
                            id="github"
                            name="github"
                            placeholder="Enter GitHub URL"
                            value={formData.github}
                            onChange={handleChange}
                        />
                        {errors.github && <p className="error">{errors.github}</p>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="profileImage">Profile Image URL:</label>
                        <input
                            type="url"
                            id="profileImage"
                            name="profileImage"
                            placeholder="Enter profile image URL"
                            value={formData.profileImage}
                            onChange={handleChange}
                        />
                        {errors.profileImage && <p className="error">{errors.profileImage}</p>}
                    </div>

                    {errors.general && <p className="error">{errors.general}</p>}

                    <button type="submit" className="save-button">Save</button>
                </form>
            </div>
        </div>
    );
};

export default EditProfile;
