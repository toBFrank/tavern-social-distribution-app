import React, { useState, useEffect } from 'react';
import { getAuthorProfile } from '../services/profileService';
import FollowButton from '../components/FollowButton';
import '../styles/pages/Profile.css';
import Cookies from 'js-cookie';
import { useNavigate, useParams } from 'react-router-dom';
import PostBox from '../components/PostBox';

const Profile = () => {
  const { authorId } = useParams();
  const currentUserId = Cookies.get('author_id');
  const [profileData, setProfileData] = useState(null);
  const [currentProfileData, setCurrentProfileData] = useState(null);
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    getAuthorProfile(authorId)
      .then((data) => {
        setProfileData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [authorId]);

  useEffect(() => {
    getAuthorProfile(currentUserId)
      .then((data) => {
        setCurrentProfileData(data);
      })
      .catch((error) => {
        console.error(error);
      });
  }, []);

  if (loading) {
    return <p>Loading...</p>;
  }

  if (!profileData) {
    return <p>Error loading profile data.</p>;
  }

  const isCurrentUser = currentUserId === authorId;

  const publicPosts = profileData.public_posts || [];
  const friendsPosts = profileData.friends_posts || [];
  const unlistedPosts = profileData.unlisted_posts || [];

  // Function to copy post link
  const handleCopyLink = (postId) => {
    const postLink = `${window.location.origin}/post/${postId}`;
    navigator.clipboard
      .writeText(postLink)
      .then((err) => console.error('Failed to copy link: ', err));
  };

  return (
    <div className="profile-page">
      <div className="profile-header">
        <div className="Img-details">
          <img
            src={profileData.profileImage}
            alt={profileData.displayName}
            className="profile-image"
          />
          {isCurrentUser ? (
            <button
              className="edit-button"
              onClick={() => navigate(`/profile/${authorId}/edit`)}
            >
              Edit Profile
            </button>
          ) : (
            <FollowButton
              authorId={authorId}
              currentUserId={currentUserId}
              currentProfileData={currentProfileData}
              profileData={profileData}
            />
          )}
        </div>

        <div className="profile-details">
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
            <div className="links-details">
              <p>
                GitHub Profile:{' '}
                <a
                  href={profileData.github ?? '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {profileData.github || 'N/A'}
                </a>
              </p>
            </div>
            <div className="links-details">
              <p>
                Profile Link:{' '}
                <a
                  href={profileData.page}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {profileData.page || 'Profile Link'}
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="posts-section">
        {isCurrentUser ? (
          <>
            <h2>Public Posts</h2>
            {publicPosts.length > 0 ? (
              publicPosts.map((post) => (
                <div key={post.id}>
                  <PostBox
                    post={post}
                    poster={profileData}
                    isUserEditable={isCurrentUser}
                  />
                  <button onClick={() => handleCopyLink(post.id)}>
                    Copy Link
                  </button>
                </div>
              ))
            ) : (
              <p>No public posts available.</p>
            )}

            <h2>Friends Posts</h2>
            {friendsPosts.length > 0 ? (
              friendsPosts.map((post) => (
                <div key={post.id}>
                  <PostBox
                    post={post}
                    poster={profileData}
                    isUserEditable={isCurrentUser}
                  />
                  <button onClick={() => handleCopyLink(post.id)}>
                    Copy Link
                  </button>
                </div>
              ))
            ) : (
              <p>No friends posts available.</p>
            )}

            <h2>Unlisted Posts</h2>
            {unlistedPosts.length > 0 ? (
              unlistedPosts.map((post) => (
                <div key={post.id}>
                  <PostBox
                    post={post}
                    poster={profileData}
                    isUserEditable={isCurrentUser}
                  />
                  <button onClick={() => handleCopyLink(post.id)}>
                    Copy Link
                  </button>
                </div>
              ))
            ) : (
              <p>No unlisted posts available.</p>
            )}
          </>
        ) : (
          <>
            <h2>Public Posts</h2>
            {publicPosts.length > 0 ? (
              publicPosts.map((post) => (
                <div key={post.id}>
                  <PostBox
                    post={post}
                    poster={profileData}
                    isUserEditable={isCurrentUser}
                  />
                  <button onClick={() => handleCopyLink(post.id)}>
                    Copy Link
                  </button>
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
