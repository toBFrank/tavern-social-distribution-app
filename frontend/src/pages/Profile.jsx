import React, { useState, useEffect } from 'react';
import { getAuthorProfile } from '../services/profileService'; 
import '../styles/pages/Profile.css';
import { useAuth } from '../contexts/AuthContext';
import editIcon from '../assets/editIcon.png';
import { updatePost } from '../services/PostsService';

const Profile = () => {
  // Get authorId from the URL parameters
  // const { authorId } = useParams();
  const { userAuthentication } = useAuth();
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  // Editing posts 
  const [editPost, setEditPost] = useState(null); 
  const [editedContent, setEditedContent] = useState(''); 


  useEffect(() => {
    // Fetch profile data when the component mounts
    getAuthorProfile(userAuthentication.authorId)
      .then((data) => {
        setProfileData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false); // Stop loading even on error
      });
  }, [userAuthentication.authorId]);

  // Show loading message or an error message if data is not available
  if (loading) {
    return <p>Loading...</p>; // Show a loading message while fetching
  }

  // Check if profileData is still null
  if (!profileData) {
    return <p>Error loading profile data.</p>; // Show an error message if data is null
  }

  // Determine if the current user is viewing their own profile
  const isCurrentUser = profileData.id === userAuthentication.authorId;

  const postTestEdit= (post) => {
    setEditPost(post.id); 
    setEditedContent(post.text_content); 
  };

  const saveEditPost = async (postId) => {
    try {
      const postToUpdate = profileData.public_posts.find(post => post.id === postId);
  
      const updatedData = {
        id: postId,  
        author_id: userAuthentication.authorId, 
        title: postToUpdate.title || "None",  
        description: postToUpdate.description || "",  
        text_content: editedContent,  
        image_content: postToUpdate.image_content || null,  
        content_type: postToUpdate.content_type || 'text/plain', 
        visibility: postToUpdate.visibility || 'PUBLIC',  
      };
  
      await updatePost(userAuthentication.authorId, postId, updatedData);
  
      setProfileData((prevData) => ({
        ...prevData,
        public_posts: prevData.public_posts.map((post) =>
          post.id === postId ? { ...post, text_content: editedContent } : post
        ),
      }));
  
      setEditPost(null);  // Exit edit mode
    } catch (err) {
      console.error('Error saving the post:', err);
    }
  };
  
  
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
          <a
            href={profileData.github}
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub Profile
          </a>
          <a href={profileData.page} target="_blank" rel="noopener noreferrer">
            Profile Link
          </a>
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
                <img
                  src={profileData.profileImage}
                  alt={profileData.displayName}
                  className="post-avatar"
                />
                <div>
                  <h3>{profileData.displayName}</h3>
                  <p>{new Date(post.published).toLocaleString()}</p>
                </div>
               <img
                  className="edit-Icon"
                  src={editIcon}
                  alt="edit"
                  onClick={() => postTestEdit(post)} 
                />
              </div>
              <div className="post-content">
              {editPost === post.id ? (
                <>
                  <textarea
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)} // edit the post
                    className="edit-textarea"
                  />
                  <button onClick={() => saveEditPost(post.id)}>Save</button> 
                </>
              ) : (
                <p>{post.text_content}</p> 
              )}
            </div>

              <div className="post-footer">
                <p>{post.like_count} Likes</p>
                <p>{post.comment_count} Comments</p>
                <p>Share</p>
              </div>
            </div>
          ))
        ) : (
          <p>This user doesn't have any public posts.</p> // Message when there are no posts
        )}
      </div>
    </div>
  );
};

export default Profile;