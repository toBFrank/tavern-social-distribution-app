import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/axios';
import { getAuthorProfile } from '../services/profileService';
import PostBox from '../components/PostBox';
import Cookies from 'js-cookie';

const PostDetail = () => {
  const { postId } = useParams(); // Get postId from URL parameters
  const [post, setPost] = useState(null);
  const [author, setAuthor] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [authorizedAuthors, setAuthorizedAuthors] = useState([]);

  useEffect(() => {
    const fetchPostDetail = async () => {
      try {
        const response = await api.get('posts/'); // Fetch all posts
        const data = response.data;
        console.log('postId:', postId);
        console.log('data.posts:', data.posts);    
        // Find the specific post using postId
        const postData = data.posts.find(post => post.id === postId);
        console.log(postData);
        if (!postData) {
          throw new Error('Post not found');
        }

        // Set authorized authors
        const postAuthorization = data.authorized_authors_per_post.find(auth => auth.post_id === postData.id);
        setAuthorizedAuthors(postAuthorization?.authorized_authors || []);

        const currentUserId = Cookies.get('author_id');

        // Check visibility and authorization
        if (
          postData.visibility === 'PUBLIC' || 
          postData.visibility === 'UNLISTED' || 
          (postAuthorization && postAuthorization.authorized_authors.includes(currentUserId))
        ) {
          setPost(postData);
          const profile = await getAuthorProfile(postData.author.id.split('/')[5]);
          setAuthor(profile);
        } else {
          setError('You are not authorized to view this post.');
        }
      } catch (err) {
        console.error('Error fetching post detail:', err.message);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPostDetail();
  }, [postId]);

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
      {/* You can add more components here like comments, likes, etc. */}
    </div>
  );
};

export default PostDetail;
