import React from 'react';
import shareButton from '../assets/shareButton.png';
import '../styles/components/ShareButton.css';
import { useNavigate } from 'react-router-dom';
import { createPost, getPostImageUrl } from '../services/PostsService';
import Cookies from 'js-cookie';

const ShareButton = ({ postId, authorId, postContent }) => {
    const navigate = useNavigate();

    const handleShareClick = async () => {
        console.log('Share button clicked');
        const storedAuthorId = Cookies.get('author_id');

        if (!storedAuthorId) {
            alert('Authorization required. Please log in.');
            navigate('/login');
            return;
        }

        const originalUrl = [authorId, postId];

        // Prepare the new post data
        const newPostData = {
            author_id: storedAuthorId,
            title: postContent.title || "Untitled",
            text_content: postContent.text_content || "",
            visibility: "SHARED", 
            content_type: postContent.content_type,
            original_url: originalUrl,
        };             

        // Check if content type is an image
        if (postContent.content_type === 'image') {
            console.log("content:", postContent);
            const imageUrl = await getPostImageUrl(postContent.author_id, postContent.id);
            console.log('Image URL:', imageUrl);
            newPostData.image_url = imageUrl;  // Add image_url to the post data
        }

        console.log("Data sent to API:", newPostData);

        try {
            const response = await createPost(storedAuthorId, newPostData);
            console.log("API Response:", response);
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
        <div className='share-container'>
            <button className='share-button' onClick={handleShareClick}>
                <img className='shareIcon' src={shareButton} alt="Share" />
                <span className="shareTxt">Share</span>
            </button>
        </div>
    );
};

export default ShareButton;
