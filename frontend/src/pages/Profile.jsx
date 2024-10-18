import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';  // Import useParams to get route parameters
import { getAuthorProfile } from '../services/profileService';  // Import service
import '../styles/pages/Profile.css';

const Profile = () => {
  // Get authorId from the URL parameters
  const { authorId } = useParams();
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
            <h2>{profileData.friends_count}</h2>
            <p>Friends</p>
          </div>
          <div>
            <h2>{profileData.followers_count}</h2>
            <p>Followers</p>
          </div>
          <div>
            <h2>{profileData.following_count}</h2>
            <p>Following</p>
          </div>
        </div>

        {/* Profile Links */}
        <div className="profile-links">
          <a href={profileData.github} target="_blank" rel="noopener noreferrer">GitHub Profile</a>
          <a href={profileData.page} target="_blank" rel="noopener noreferrer">Profile Link</a>
        </div>

        {/* Follow / Edit Profile Button */}
        {isCurrentUser ? (
          <button>Edit Profile</button>
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
                <p>{post.content}</p>
              </div>
              <div className="post-footer">
                <p>{post.like_count} Likes</p>
                <p>{post.comment_count} Comments</p>
                <p>Share</p>
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
