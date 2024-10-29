import React from 'react';
import shareButton from '../assets/shareButton.png';
import '../styles/components/ShareButton.css';
import { useNavigate } from 'react-router-dom';

const ShareButton = ({ postId, authorId }) => {
    const navigate = useNavigate();
    // console.log('Author ID:', authorId);
    const handleShareClick = () => {
        navigate(`/post/${postId}/share`, { state: { postId: postId, authorId: authorId } });
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
