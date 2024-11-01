import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import api from '../services/axios';
import { getAuthorProfile } from '../services/profileService';
import PostBox from '../components/PostBox';
import Cookies from 'js-cookie';

const PostDetail = () => {
  const { postFqid } = useParams(); // Get the postFqid from the URL
  const location = useLocation(); // Use location to get passed state
  const [post, setPost] = useState(null);
  const [author, setAuthor] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get authorized authors passed from the Home component
  const authorizedAuthors = location.state?.authorizedAuthors || [];

  useEffect(() => {
    const fetchPostDetail = async () => {
      try {
        const response = await api.get(`posts/${postFqid}/`); // Fetch post detail
        const postData = response.data; // Get the post data

        // Check if the current user is an authorized author
        const currentAuthorId = Cookies.get('author_id');
        if (
          postData.visibility === 'PUBLIC' || 
          postData.visibility === 'UNLISTED' || 
          authorizedAuthors.includes(currentAuthorId) // Check if the user is authorized
        ) {
          setPost(postData); // Set the post data if visibility is allowed
          const profile = await getAuthorProfile(postData.author_id); // Fetch the author profile
          setAuthor(profile); // Set the author data
        } else {
          setError('This post is not allowed to be viewed.'); // Set error message for disallowed posts
        }
      } catch (err) {
        console.error('Error fetching post detail:', err.message);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPostDetail();
  }, [postFqid, authorizedAuthors]); // Depend on postFqid and authorizedAuthors

  if (loading) {
    return <p>Loading...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  return (
    <div>
      {post && author && (
        <PostBox post={post} poster={author} />
      )}
      {/* Add more components as needed, e.g., comments, likes, etc. */}
    </div>
  );
};

export default PostDetail;
