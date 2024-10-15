import React, { useState, useRef } from 'react'; 
import './Post.css';
import { ReactComponent as ImageUploader } from './../Images/imageUploader.svg';

const Post = () => {
    const [visibility, setVisibility] = useState('public'); 
    const [selectedOption, setSelectedOption] = useState('Plain'); 
    const [uploadedImage, setUploadedImage] = useState(null); 
    const fileInputUpload = useRef(null); 

    const handleVisibilityChange = (event) => {
        setVisibility(event.target.value); 
    };

    const handleOptionClick = (option) => {
        setSelectedOption(option); 
    };

    const handleImageUploaderClick = () => {
        fileInputUpload.current.click(); 
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            const imageUrl = URL.createObjectURL(file);
            setUploadedImage(imageUrl); 
        }
    };

    return (
        <div className='posts-page'>
            <div className='top-container'>
                <h1>Post</h1>
                <div className='posts-options'>
                    <h3 
                        className={selectedOption === 'Plain' ? 'active-option' : 'inactive-option'}
                        onClick={() => handleOptionClick('Plain')}
                    >
                        Plain
                    </h3>
                    <h3 
                        className={selectedOption === 'Markdown' ? 'active-option' : 'inactive-option'}
                        onClick={() => handleOptionClick('Markdown')}
                    >
                        Markdown
                    </h3>
                    <h3 
                        className={selectedOption === 'Image' ? 'active-option' : 'inactive-option'}
                        onClick={() => handleOptionClick('Image')}
                    >
                        Image
                    </h3>
                </div>
            </div>

            {selectedOption === 'Image' ? (
                <>
                    {uploadedImage ? (
                        <img 
                            src={uploadedImage} 
                            alt="Uploaded" 
                            className="uploaded-image" 
                            onClick={handleImageUploaderClick} 
                        />
                    ) : (
                        <ImageUploader className="image-uploader-svg" onClick={handleImageUploaderClick} />
                    )}
                    <input 
                        type="file" 
                        ref={fileInputUpload} 
                        style={{ display: 'none' }} 
                        onChange={handleFileChange} 
                    />
                </>
            ) : (
                <textarea placeholder='Type something here...'></textarea>
            )}

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
