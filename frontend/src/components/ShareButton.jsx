import React from 'react';
import shareButton from '../assets/shareButton.png';
import '../styles/components/ShareButton.css';
import { useNavigate } from 'react-router-dom';
import { createPost, getPostImageUrl } from '../services/PostsService';
import Cookies from 'js-cookie';

const ShareButton = ({ postId, authorId, postContent }) => {
  const navigate = useNavigate();

  function removeBase64Prefix(base64) {
    // Define the prefixes to look for
    const prefixes = [
      'data:image/png;base64,',
      'data:image/jpeg;base64,',
      'data:image/gif;base64,',
    ];

    for (const prefix of prefixes) {
      if (base64.startsWith(prefix)) {
        return base64.substring(prefix.length);
      }
    }

    return base64;
  }

  const handleShareClick = async () => {
    console.log('Share button clicked');
    const storedAuthorId = Cookies.get('author_id');

    if (!storedAuthorId) {
      alert('Authorization required. Please log in.');
      navigate('/login');
      return;
    }

    const originalUrl = [authorId, postId];

    const unlabeledBase64Img = removeBase64Prefix(postContent.content ?? '');

    const sharedPostData = {
      author: storedAuthorId,
      title: postContent.title || 'Untitled',
      content: unlabeledBase64Img || '',
      visibility: 'SHARED',
      contentType: postContent.contentType,
      original_url: originalUrl,
    };

    // Check if content type is an image
    if (postContent.contentType.startsWith('image/')) {
      console.log('content:', postContent);
      const imageUrl = await getPostImageUrl(
        postContent.author.id.split('/')[5],
        postContent.id
      );
      // console.log('Image URL:', imageUrl);
      sharedPostData.image_url = imageUrl; // Add image_url to the post data
    }

    console.log('Data sent to API:', sharedPostData);

    try {
      const response = await createPost(storedAuthorId, sharedPostData);
      // console.log("API Response:", response);
      console.log('Response Data:', response.data);
      alert('Post shared successfully!');
    } catch (error) {
      if (error.response && error.response.status === 401) {
        alert('Authorization failed. Please log in again.');
        navigate('/login');
      } else {
        console.error('Error sharing post:', error);
        alert('Failed to share the post. Check console for details.');
      }
    }
  };

  return (
    <div className="share-container">
      <button className="share-button" onClick={handleShareClick}>
        <img className="shareIcon" src={shareButton} alt="Share" />
        <span className="shareTxt">Share</span>
      </button>
    </div>
  );
};

export default ShareButton;
