import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';  // Import useParams to get route parameters
import { getAuthorProfile } from '../services/profileService';  // Import service
import '../styles/pages/Profile.css';

const Profile = () => {
  // Get authorId from the URL parameters
  const { authorId } = useParams();
  const navigate = useNavigate();  // Initialize useNavigate
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch profile data when the component mounts
    getAuthorProfile(authorId)
      .then(data => {
        setProfileData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);  // Stop loading even on error
      });
  }, [authorId]);

  // Show loading message or an error message if data is not available
  if (loading) {
    return <p>Loading...</p>;  // Show a loading message while fetching
  }

  // Check if profileData is still null
  if (!profileData) {
    return <p>Error loading profile data.</p>; // Show an error message if data is null
  }

  // Determine if the current user is viewing their own profile
  const isCurrentUser = profileData.id === authorId;

  return (
    <div className="profile-page">
      {/* Profile Header */}
      <div className="profile-header">
        <img src={profileData.profileImage} alt={profileData.displayName} className="profile-image" />
        <h1>{profileData.displayName}</h1>

        <div className="profile-stats">
          <div>
            <h2>{profileData.friends_count || 0}</h2>
            <p>Friends</p>
          </div>
          <div>
            <h2>{profileData.followers_count || 0}</h2>
            <p>Followers</p>
          </div>
          <div>
            <h2>{profileData.following_count || 0}</h2>
            <p>Following</p>
          </div>
        </div>

        {/* Profile Links */}
        <div className="profile-links">
          <p>GitHub Profile: <a href={profileData.github} target="_blank" rel="noopener noreferrer">{profileData.github}</a></p>
          <p>Profile Link: <a href={profileData.page} target="_blank" rel="noopener noreferrer">{profileData.page}</a></p>
        </div>

        {/* Follow / Edit Profile Button */}
        {isCurrentUser ? (
          <button onClick={() => navigate(`/authors/${authorId}/profile/edit`)}>Edit Profile</button>
        ) : (
          <button>Follow</button>
        )}
      </div>

      {/* Public Posts Section */}
      <div className="posts-section">
        {profileData.public_posts && profileData.public_posts.length > 0 ? (
          profileData.public_posts.map((post) => (
            <div key={post.id} className="post">
              <div className="post-header">
                <img src={profileData.profileImage} alt={profileData.displayName} className="post-avatar" />
                <div>
                  <h3>{profileData.displayName}</h3>
                  <p>{new Date(post.published).toLocaleString()}</p>
                </div>
              </div>
              <div className="post-content">
                <p>{post.description}</p> {/* Updated to display description */}
              </div>
              <div className="post-footer">
                <p>{profileData.likes_count || 0} Likes</p>  {/* Display likes count */}
                <p>{profileData.comments_count || 0} Comments</p>  {/* Display comments count */}
              </div>
            </div>
          ))
        ) : (
          <p>This user doesn't have any public posts.</p>  // Message when there are no posts
        )}
      </div>
    </div>
  );
};

export default Profile;
