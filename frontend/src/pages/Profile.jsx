import React, { useState, useEffect } from 'react';
import { getAuthorProfile } from '../services/profileService';
import FollowButton from '../components/FollowButton';
import '../styles/pages/Profile.css';
import Cookies from 'js-cookie';
import { useNavigate, useParams } from 'react-router-dom';
import PostBox from '../components/PostBox';
import { getFollowers } from '../services/FollowDetailService';
import { getFriends } from '../services/FriendsDetailService';
import { getFollowing } from '../services/FollowingDetailService';


const Profile = () => {
  const { authorId } = useParams();
  const currentUserId = Cookies.get('author_id');
  const [profileData, setProfileData] = useState(null);
  const [currentProfileData, setCurrentProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [followers, setFollowers] = useState([]);
  const [friends, setFriends] = useState([]); // State for friends
  const [following, setFollowing] = useState([]);
  const [showFollowers, setShowFollowers] = useState(false);
  const [showFriends, setShowFriends] = useState(false);
  const [showFollowing, setShowFollowing] = useState(false);


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

  // Function to fetch followers and toggle the display
  const handleFollowersClick = async () => {
    try {
      const followersData = await getFollowers(authorId);
      setFollowers(followersData.followers);
      setShowFollowers(!showFollowers);  // Toggle visibility
      setShowFriends(false); // Close followers modal if open
      setShowFollowing(false);
    } catch (error) {
      console.error("Error fetching followers:", error);
    }
  };
  // Function to fetch friends and toggle the display
  const handleFriendsClick = async () => {
    try {
      const friendsData = await getFriends(authorId);
      setFriends(friendsData.friends);
      setShowFriends(!showFriends); // Toggle visibility
      setShowFollowers(false); // Close followers modal if open
      setShowFollowing(false);
    } catch (error) {
      console.error("Error fetching friends:", error);
    }
  };

  const handleFollowingClick = async () => {
    try {
      const followingData = await getFollowing(authorId);
      setFollowing(followingData.following);
      setShowFollowing(!showFollowing); // Toggle visibility
      setShowFollowers(false); // Close followers modal if open
      setShowFriends(false);
    } catch (error) {
      console.error("Error fetching following:", error);
    }
  };
  
  

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
  const sharedPosts = profileData.shared_posts || [];
  const UnlistedAndSharesPosts = [...unlistedPosts, ...sharedPosts];

  // Function to copy post link
  const handleCopyLink = (postId) => {
    const postLink = `${window.location.origin}/post/${postId}`;
    navigator.clipboard.writeText(postLink).catch(
      (err) => console.error('Failed to copy link: ', err)
    );
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
            <button className="edit-button" onClick={() => navigate(`/profile/${authorId}/edit`)}>Edit Profile</button>
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
              <h2 style={{ cursor: 'pointer' }} onClick={handleFriendsClick}>
                {profileData.friends_count || 0}
              </h2>
              <p>Friends</p>
            </div>
            <div>
              <h2 style={{ cursor: 'pointer' }} onClick={handleFollowersClick}>
                {profileData.followers_count || 0}
              </h2>
              <p>Followers</p>
            </div>
            <div>
            <h2 style={{ cursor: 'pointer' }} onClick={handleFollowingClick}>
                {profileData.following_count || 0}
              </h2>
              <p>Following</p>
            </div>
          </div>

          {/* Profile Links */}
          <div className="profile-links">
            <div className="links-details">
              <p>GitHub Profile:</p>
              <a href={profileData.github} target="_blank" rel="noopener noreferrer">
                {profileData.github || 'GitHub Profile'}
              </a>
            </div>
            <div className="links-details">
              <p>Profile Link:</p>
              <a href={profileData.page} target="_blank" rel="noopener noreferrer">
                {profileData.page || 'Profile Link'}
              </a>
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
                  <PostBox post={post} poster={profileData} isUserEditable={isCurrentUser} />
                  <button onClick={() => handleCopyLink(post.id)}>Copy Link</button>
                </div>
              ))
            ) : (
              <p>No public posts available.</p>
            )}

            <h2>Friends Posts</h2>
            {friendsPosts.length > 0 ? (
              friendsPosts.map((post) => (
                <div key={post.id}>
                  <PostBox post={post} poster={profileData} isUserEditable={isCurrentUser} />
                  <button onClick={() => handleCopyLink(post.id)}>Copy Link</button>
                </div>
              ))
            ) : (
              <p>No friends posts available.</p>
            )}

            <h2>Unlisted Posts</h2>
            {UnlistedAndSharesPosts.length > 0 ? (
              UnlistedAndSharesPosts.sort((a, b) => new Date(b.published) - new Date(a.published)).map((post) => {
                // console.log('Unlisted Post:', post);
                return (
                  <div key={post.id}>
                    <PostBox post={post} poster={profileData} isUserEditable={isCurrentUser} />
                    <button onClick={() => handleCopyLink(post.id)}>Copy Link</button>
                  </div>
                );
              })
            ) : (
              <p>No unlisted or shared posts available.</p>
            )}
            </>
          ) : (
          <>
            <h2>Public Posts</h2>
            {publicPosts.length > 0 ? (
              publicPosts.map((post) => (
                <div key={post.id}>
                  <PostBox post={post} poster={profileData} isUserEditable={isCurrentUser} />
                  <button onClick={() => handleCopyLink(post.id)}>Copy Link</button>
                </div>
              ))
            ) : (
              <p>This user doesn't have any public posts.</p>
            )}
          </>
        )}
      </div>

      {showFollowers && (
  <div className="followers-modal">
    <h3 style={{ textAlign: 'center' }}>Followers</h3>
    <div className="followers-list">
      {followers.length > 0 ? (
        followers.map((follower) => (
          <div 
            className="follower-item" 
            key={follower.id} 
            onClick={() => {
              setShowFollowers(false); // Close the modal first
              navigate(`/profile/${follower.id}`); // Then navigate to follower's profile
            }} 
            style={{ cursor: 'pointer' }} // Change cursor to pointer to indicate it's clickable
          >
            <span className="follower-name">{follower.displayName}</span>
          </div>
        ))
      ) : (
        <div className="follower-item">
          <span className="follower-name">No followers found.</span>
        </div>
      )}
    </div>
    <button onClick={() => setShowFollowers(false)} style={{ display: 'block', margin: '10px auto' }}>
      Close
    </button>
  </div>
)}
 {/* Friends Modal */}
 {showFriends && (
        <div className="friends-modal">
          <h3 style={{ textAlign: 'center' }}>Friends</h3>
          <div className="friends-list">
            {friends.length > 0 ? (
              friends.map((friend) => (
                <div 
                  className="friend-item" 
                  key={friend.id} 
                  onClick={() => {
                    setShowFriends(false); // Close the modal first
                    navigate(`/profile/${friend.id}`); // Then navigate to friend's profile
                  }} 
                  style={{ cursor: 'pointer' }} // Change cursor to pointer to indicate it's clickable
                >
                  <span className="friend-name">{friend.displayName}</span>
                </div>
              ))
            ) : (
              <div className="friend-item">
                <span className="friend-name">No friends found.</span>
              </div>
            )}
          </div>
          <button onClick={() => setShowFriends(false)} style={{ display: 'block', margin: '10px auto' }}>
            Close
          </button>
        </div>
      )}

      {/* Following Modal */}
 {showFollowing && (
        <div className="following-modal">
          <h3 style={{ textAlign: 'center' }}>Following</h3>
          <div className="following-list">
            {following.length > 0 ? (
              following.map((following) => (
                <div 
                  className="following-item" 
                  key={following.id} 
                  onClick={() => {
                    setShowFollowing(false); // Close the modal first
                    navigate(`/profile/${following.id}`); // Then navigate to friend's profile
                  }} 
                  style={{ cursor: 'pointer' }} // Change cursor to pointer to indicate it's clickable
                >
                  <span className="following-name">{following.displayName}</span>
                </div>
              ))
            ) : (
              <div className="following-item">
                <span className="following-name">No Following found.</span>
              </div>
            )}
          </div>
          <button onClick={() => setShowFollowing(false)} style={{ display: 'block', margin: '10px auto' }}>
            Close
          </button>
        </div>
      )}


    </div>
  );
};

export default Profile;
