import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import api from '../services/axios';
import { getAuthorProfile } from '../services/profileService';
import PostBox from '../components/PostBox';
import Cookies from 'js-cookie';

const PostDetail = () => {
  const { postFqid } = useParams();
  const location = useLocation();
  const [post, setPost] = useState(null);
  const [author, setAuthor] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const authorizedAuthors = useMemo(() => location.state?.authorizedAuthors || [], [location.state]);

  const postFromState = location.state?.post;

  useEffect(() => {
    const fetchPostDetail = async () => {
      if (postFromState) {
        setPost(postFromState);
        const profile = await getAuthorProfile(postFromState.author_id);
        setAuthor(profile);
        setLoading(false);
        return;
      }

      try {
        const response = await api.get(`posts/${postFqid}/`);
        if (!response || !response.data) {
          throw new Error("Post data is unavailable");
        }

        const postData = response.data;

        const currentAuthorId = Cookies.get('author_id');
        if (
          postData.visibility === 'PUBLIC' || 
          postData.visibility === 'UNLISTED' || 
          authorizedAuthors.includes(currentAuthorId)
        ) {
          setPost(postData);
          const profile = await getAuthorProfile(postData.author_id);
          setAuthor(profile);
        } else {
          setError('This post is not allowed to be viewed.');
        }
      } catch (err) {
        console.error('Error fetching post detail:', err.message);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPostDetail();
  }, [postFqid, authorizedAuthors, postFromState]);

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
      {/* Additional components like comments, likes, etc. */}
    </div>
  );
};

export default PostDetail;
