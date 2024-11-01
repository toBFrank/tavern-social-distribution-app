import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom'; // Import Link from React Router
import { getMarkdownText } from '../utils/getMarkdownText';
import { getPostImageUrl } from '../services/PostsService';
import '../styles/components/PostBox.css';
import LikeButton from './LikeButton';
import CommentsModal from './CommentsModal';
import { BorderColor } from "@mui/icons-material";
import { useNavigate } from 'react-router-dom';

const PostBox = ({ post, poster, isUserEditable }) => {
  const [imageUrl, setImageUrl] = useState(null);

  const posterName = poster ? poster.displayName : 'Anonymous';
  const posterImageUrl = poster ? poster.profileImage : null;
  const navigate = useNavigate();

  useEffect(() => {
    const getImgUrlFromServer = async () => {
      try {
        const imageUrlFromServer = await getPostImageUrl(
          post.author_id,
          post.id
        );
        setImageUrl(imageUrlFromServer);
      } catch {
        setImageUrl(null);
      }
    };
    if (post.content_type === 'image') {
      getImgUrlFromServer();
    }
  }, []);

  return (
    <div className="post-box">
      <div className="post-header">
        <Link to={`/profile/${post.author_id}`} style={{ display: 'flex' }}> {/* Add display: flex */}
          <div className="profile-image-container">
            {posterImageUrl ? (
              <img src={posterImageUrl} alt="profile" className="profile-image" />
            ) : (
              <div className="profile-image-default" />
            )}
          </div>
        </Link>
        <div className="poster-name-date">
          <h4>{posterName}</h4>
          <p>{new Date(post.published).toLocaleString()}</p>
        </div>
        {isUserEditable && (
          <div className='post-edit'>
            <button className='post-edit-button' onClick={() => navigate(`/post/${post.id}/edit`, { state: { postId: post.id } })}>
              <BorderColor className='post-edit-icon' />
            </button>
          </div>
        )}
      </div>
      <div className="post-content">
        <h2>{post.title}</h2>
        {post.content_type === 'text/plain' && <p>{post.text_content}</p>}
        {post.content_type === 'image' && <img src={imageUrl} alt="post" />}
        {post.content_type === 'text/markdown' && (
          <div dangerouslySetInnerHTML={getMarkdownText(post.text_content)} />
        )}
      </div>
      <div className="post-footer">
        <LikeButton postId={post.id} />
        <CommentsModal postId={post.id} />
      </div>
    </div>
  );
};

export default PostBox;
