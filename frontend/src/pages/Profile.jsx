import React, { useState, useEffect } from 'react';
import { getAuthorProfile } from '../services/profileService'; // Import service
import FollowButton from '../components/FollowButton';
import '../styles/pages/Profile.css';
import editIcon from '../assets/editIcon.png';
import Cookies from 'js-cookie';
import { useNavigate, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';  // Import react-markdown for rendering markdown content
import PostBox from '../components/PostBox';

const Profile = () => {
  const { authorId } = useParams();  // Get the authorId from the URL parameters
  const currentUserId = Cookies.get('author_id');  // Get the current user's ID from cookies
  const [profileData, setProfileData] = useState(null);
  const [currentProfileData, setCurrentProfileData] = useState(null);
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

  useEffect(() => {
    getAuthorProfile(currentUserId)
      .then((data) => {
        setCurrentProfileData(data);
      })
      .catch((error) => {
        console.error(error);
      })
  }, []) //empty dependency list so that its only called once when component mounts

  
  // Show loading message or an error message if data is not available
  if (loading) {
    return <p>Loading...</p>; // Show a loading message while fetching
  }

  if (!profileData) {
    return <p>Error loading profile data.</p>; // Show an error message if data is null
  }

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
          <FollowButton 
            authorId={authorId} 
            currentUserId={currentUserId} 
            currentProfileData={currentProfileData} 
            profileData={profileData}
          />
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
                <PostBox post={post} poster={profileData} />
              ))
            ) : (
              <p>No public posts available.</p>
            )}

            {/* Friends Posts */}
            <h2>Friends Posts</h2>
            {friendsPosts.length > 0 ? (
              friendsPosts.map((post) => (
                <PostBox post={post} poster={profileData} />
              ))
            ) : (
              <p>No friends posts available.</p>
            )}

            {/* Unlisted Posts */}
            <h2>Unlisted Posts</h2>
            {unlistedPosts.length > 0 ? (
              unlistedPosts.map((post) => (
                <PostBox post={post} poster={profileData} />
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
                <PostBox post={post} poster={profileData} />
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

