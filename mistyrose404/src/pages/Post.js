import React, { useState } from 'react'; 
import './Post.css';

const Post = () => {
    const [visibility, setVisibility] = useState('public'); 

    const handleVisibilityChange = (event) => {
        setVisibility(event.target.value); 
    };

    return (
        <div className='posts-page'>
            <div className='top-container'>
                <h1>Post</h1>
                <div className='posts-options'>
                    <h3>Plain</h3>
                    <h3>Markdown</h3>
                    <h3>Image</h3>
                </div>
            </div>
            <textarea placeholder='Type something here...'></textarea>
            <div className='visibility-options'>
                <label>
                    <input 
                        type="radio" 
                        value="public" 
                        checked={visibility === 'public'} 
                        onChange={handleVisibilityChange} 
                    />
                    Public
                </label>
                <label>
                    <input 
                        type="radio" 
                        value="friends" 
                        checked={visibility === 'friends'} 
                        onChange={handleVisibilityChange} 
                    />
                    Friends
                </label>
                <label>
                    <input 
                        type="radio" 
                        value="unlisted" 
                        checked={visibility === 'unlisted'} 
                        onChange={handleVisibilityChange} 
                    />
                    Unlisted
                </label>
            </div>
            <div className='postPage-buttons'>
                <button className='post-button'>
                Post
                </button>
                <button className='delete-button'>
                    Delete
                </button>
            </div>

        </div>
    );
}

export default Post;
