import React, { useState, useRef } from 'react';
import '../styles/pages/Post.css';
import { ReactComponent as ImageUploader } from './../assets/imageUploader.svg';
import MarkdownEditor from '../components/MarkdownEditor';
import { createPost } from '../services/PostsService';
import Cookies from 'js-cookie';

const Post = () => {
  //#region Properties
  const authorId = Cookies.get('author_id');

  const [visibility, setVisibility] = useState('public');
  const [selectedOption, setSelectedOption] = useState('Plain');

  const options = ['Plain', 'Markdown', 'Image'];
  const [uploadedImage, setUploadedImage] = useState(null);
  const fileInputUpload = useRef(null);
  const [plainText, setPlainText] = useState('');
  const [markdown, setMarkdown] = useState('');

  //#endregion

  //#region Event Handlers
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
  const handlePlainTextChange = (event) => {
    setPlainText(event.target.value);
  };

  const handlePostClick = async () => {
    const postData = {
      author_id: authorId,
      title: 'My Post', // TODO: Add title
      text_content:
        selectedOption === 'Plain'
          ? plainText
          : selectedOption === 'Markdown'
            ? markdown
            : null,
      image_content: selectedOption === 'Image' ? uploadedImage : null,
      content_type:
        selectedOption === 'Image'
          ? 'image'
          : selectedOption === 'Markdown'
            ? 'text/markdown'
            : 'text/plain',
      visibility: visibility.toUpperCase(),
    };

    try {
      // print all cookies
      console.log(Cookies.get());
      const response = await createPost(authorId, postData);
      console.log(response);
    } catch (error) {
      console.error(error);
    }
  };
  //#endregion

  //#region Functions
  //#endregion

  //#region Render
  const renderOption = (option) => (
    <h3
      key={option}
      className={
        selectedOption === option ? 'active-option' : 'inactive-option'
      }
      onClick={() => handleOptionClick(option)}
    >
      {option}
    </h3>
  );
  //#endregion

  return (
    <div className="posts-page">
      <div className="top-container">
        <h1>Post</h1>
        <div className={'posts-options'}>{options.map(renderOption)}</div>
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
            <ImageUploader
              className="image-uploader-svg"
              onClick={handleImageUploaderClick}
            />
          )}
          <input
            type="file"
            ref={fileInputUpload}
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
        </>
      ) : selectedOption === 'Plain' ? (
        <textarea
          className="plain-textarea"
          placeholder="Type something here..."
          value={plainText}
          onChange={handlePlainTextChange}
        ></textarea>
      ) : (
        <MarkdownEditor markdown={markdown} setMarkdown={setMarkdown} />
      )}

      <div className="visibility-options">
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
      <div className="postPage-buttons">
        <button className="post-button" onClick={handlePostClick}>
          Post
        </button>
        {/* <button className="delete-button">Delete</button> */}
      </div>
    </div>
  );
};

export default Post;
