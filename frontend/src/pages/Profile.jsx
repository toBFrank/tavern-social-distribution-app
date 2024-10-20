import React, { useState, useEffect } from 'react';
import { getAuthorProfile } from '../services/profileService'; // Import service
import '../styles/pages/Profile.css';
import Cookies from 'js-cookie';
import { useNavigate, useParams } from 'react-router-dom';

const Profile = () => {
  const { authorId } = useParams();  // Get the authorId from the URL parameters
  const currentUserId = Cookies.get('author_id');  // Get the current user's ID from cookies
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    // Fetch profile data when the component mounts
    getAuthorProfile(authorId)
      .then((data) => {
        setProfileData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false); // Stop loading even on error
      });
  }, [authorId]);

  // Show loading message or an error message if data is not available
  if (loading) {
    return <p>Loading...</p>; // Show a loading message while fetching
  }

  if (!profileData) {
    return <p>Error loading profile data.</p>; // Show an error message if data is null
  }

  // Determine if the current user is viewing their own profile
  const isCurrentUser = currentUserId === authorId;

  // Filter posts based on visibility
  const publicPosts = profileData.public_posts || [];
  const friendsPosts = profileData.friends_posts || [];
  const unlistedPosts = profileData.unlisted_posts || [];

  return (
    <div className="profile-page">
      {/* Profile Header */}
      <div className="profile-header">
        <img
          src={profileData.profileImage}
          alt={profileData.displayName}
          className="profile-image"
        />
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
          <p>GitHub Profile:</p>
          <a
            href={profileData.github}
            target="_blank"
            rel="noopener noreferrer"
          >
            {profileData.github || 'GitHub Profile'}
          </a>
          <p>Profile Link:</p>
          <a href={profileData.page} target="_blank" rel="noopener noreferrer">
            {profileData.page || 'Profile Link'}
          </a>
        </div>

        {/* Follow / Edit Profile Button */}
        {isCurrentUser ? (
          <button onClick={() => navigate(`/profile/${authorId}/edit`)}>Edit Profile</button>
        ) : (
          <button>Follow</button>
        )}
      </div>

      {/* Post Sections */}
      <div className="posts-section">
        {/* If it's the current user's profile, show all post sections (Public, Friends, Unlisted) */}
        {isCurrentUser ? (
          <>
            {/* Public Posts */}
            <h2>Public Posts</h2>
            {publicPosts.length > 0 ? (
              publicPosts.map((post) => (
                <div key={post.id} className="post">
                  <div className="post-header">
                    <img src={profileData.profileImage} alt={profileData.displayName} className="post-avatar" />
                    <div>
                      <h3>{profileData.displayName}</h3>
                      <p>{new Date(post.published).toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="post-content">
                    <h4>{post.title || "Untitled"}</h4> {/* Display the post title */}
                    <p>{post.text_content || "No content available"}</p> {/* Display the text_content */}
                  </div>
                  <div className="post-footer">
                    <p>{post.likes_count} Likes</p>
                    <p>{post.comments_count} Comments</p>
                  </div>
                </div>
              ))
            ) : (
              <p>No public posts available.</p>
            )}

            {/* Friends Posts */}
            <h2>Friends Posts</h2>
            {friendsPosts.length > 0 ? (
              friendsPosts.map((post) => (
                <div key={post.id} className="post">
                  <div className="post-header">
                    <img src={profileData.profileImage} alt={profileData.displayName} className="post-avatar" />
                    <div>
                      <h3>{profileData.displayName}</h3>
                      <p>{new Date(post.published).toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="post-content">
                    <h4>{post.title || "Untitled"}</h4> {/* Display the post title */}
                    <p>{post.text_content || "No content available"}</p> {/* Display the text_content */}
                  </div>
                  <div className="post-footer">
                    <p>{post.likes_count} Likes</p>
                    <p>{post.comments_count} Comments</p>
                  </div>
                </div>
              ))
            ) : (
              <p>No friends posts available.</p>
            )}

            {/* Unlisted Posts */}
            <h2>Unlisted Posts</h2>
            {unlistedPosts.length > 0 ? (
              unlistedPosts.map((post) => (
                <div key={post.id} className="post">
                  <div className="post-header">
                    <img src={profileData.profileImage} alt={profileData.displayName} className="post-avatar" />
                    <div>
                      <h3>{profileData.displayName}</h3>
                      <p>{new Date(post.published).toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="post-content">
                    <h4>{post.title || "Untitled"}</h4> {/* Display the post title */}
                    <p>{post.text_content || "No content available"}</p> {/* Display the text_content */}
                  </div>
                  <div className="post-footer">
                    <p>{post.likes_count} Likes</p>
                    <p>{post.comments_count} Comments</p>
                  </div>
                </div>
              ))
            ) : (
              <p>No unlisted posts available.</p>
            )}
          </>
        ) : (
          <>
            {/* Only Public Posts if it's someone else's profile */}
            <h2>Public Posts</h2>
            {publicPosts.length > 0 ? (
              publicPosts.map((post) => (
                <div key={post.id} className="post">
                  <div className="post-header">
                    <img src={profileData.profileImage} alt={profileData.displayName} className="post-avatar" />
                    <div>
                      <h3>{profileData.displayName}</h3>
                      <p>{new Date(post.published).toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="post-content">
                    <h4>{post.title || "Untitled"}</h4> {/* Display the post title */}
                    <p>{post.text_content || "No content available"}</p> {/* Display the text_content */}
                  </div>
                  <div className="post-footer">
                    <p>{post.likes_count} Likes</p>
                    <p>{post.comments_count} Comments</p>
                  </div>
                </div>
              ))
            ) : (
              <p>This user doesn't have any public posts.</p>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Profile;
