import React, { useEffect, useState } from 'react';
import { getMarkdownText } from '../utils/getMarkdownText';
import { getPostImageUrl, getPost, getPostByFqid } from '../services/PostsService';
import { getAuthorProfile } from '../services/profileService';
import '../styles/components/PostBox.css';
import LikeButton from './LikeButton';
import CommentsModal from './CommentsModal';
import ShareButton from './ShareButton';
import { BorderColor } from "@mui/icons-material";
import { useNavigate } from 'react-router-dom';

const PostBox = ({ post, poster, isUserEditable }) => {
  const [imageUrl, setImageUrl] = useState(null);
  const [originalPost, setOriginalPost] = useState(null);
  const [originalAuthor, setOriginalAuthor] = useState(null);
  const [originalImageUrl, setOriginalImageUrl] = useState(null);
  const [posterImageUrl, setPosterImageUrl] = useState(poster ? poster.profileImage : null);
  const posterName = originalPost ? originalAuthor?.displayName : poster?.displayName || 'Anonymous';
  const postPublishedDate = originalPost ? originalPost.published : post.published;
  const navigate = useNavigate();

  useEffect(() => {
    const getImgUrlFromServer = async () => {
      // console.log(JSON.stringify(post));
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
    if (post.content_type === 'image' & post.visibility !== 'SHARED') {
      getImgUrlFromServer();
    } 
  }, [post.author_id, post.content_type, post.id]);

  // Fetch post have visibility of SHARED it will take the original posts info
  useEffect(() => {
    const fetchSharedPostDetails = async () => {
        if (post.visibility === 'SHARED' && post.original_url) {
            try {
                const response = await getPost(post.original_url[0], post.original_url[1]);
                setOriginalPost(response.data);
                
                // Fetch the original image URL if the post type is an image
                if (response.data.content_type === 'image') {
                    const originalImgUrl = await getPostImageUrl(response.data.author_id, response.data.id);
                    setOriginalImageUrl(originalImgUrl);
                }
            } catch (error) {
                console.error('Error fetching shared post:', error);
            }
        }
    };

    fetchSharedPostDetails();
  }, [post.visibility, post.original_url]);

  
  // Fetch original author's profile once originalPost is set
  useEffect(() => {
    const fetchOriginalAuthorProfile = async () => {
      if (originalPost) {
        try {
          const authorProfile = await getAuthorProfile(originalPost.author_id);
          // console.log('orig post url: ', post.visibility);
          setOriginalAuthor(authorProfile);
  
          // Set poster image if originalAuthor has a profile image
          if (authorProfile.profileImage) {
            setPosterImageUrl(authorProfile.profileImage);
          }
        } catch (error) {
          console.error("Error fetching original author profile:", error);
        }
      }
    };
  
    fetchOriginalAuthorProfile();
  }, [originalPost]);

  return (
    <div className="post-box">
        {originalPost && (
          <div className="poster-author-header">
            <p>Reposted By: {poster.displayName}</p>
            <p>{new Date(post.published).toLocaleString()}</p>
          </div>
        )}
      <div className="post-header">
        {posterImageUrl ? (
          <div className="profile-image-container">
            <img src={posterImageUrl} alt="profile" className="profile-image" />
          </div>
        ) : (
          <div className="profile-image-default" />
        )}
        <div className="poster-name-date">
          <h4>{posterName}</h4>
          <p>{new Date(postPublishedDate).toLocaleString()}</p>
        </div>
        {isUserEditable && post.visibility !== 'SHARED' && (
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
          {post.content_type === 'image' && (
              originalPost && post.visibility === 'SHARED' ? (
                  <img src={originalImageUrl} alt="post share" />
              ) : (
                  <img src={imageUrl} alt="post" />
              )
          )}
          {post.content_type === 'text/markdown' && (
              <div dangerouslySetInnerHTML={getMarkdownText(post.text_content)} />
          )}
      </div>

      <div className="post-footer">
        <LikeButton postId={post.id} />
        <CommentsModal postId={post.id} />
        {(post.visibility !== 'FRIENDS' && post.visibility !== 'UNLISTED' && post.visibility !== 'SHARED') && (
          <ShareButton postId={post.id} authorId={post.author_id} postContent={post} />
        )}
      </div>
    </div>
  );
};

export default PostBox;
