import React, { useState, useRef } from 'react';
import '../styles/pages/Post.css';
import { ReactComponent as ImageUploader } from './../assets/imageUploader.svg';
import MarkdownEditor from '../components/MarkdownEditor';
import { createPost, deletePost } from '../services/PostsService';
import Cookies from 'js-cookie';
import { useNavigate } from 'react-router-dom';

const Post = ({ postId }) => {
  //#region Properties
  const authorId = Cookies.get('author_id');

  const navigate = useNavigate();
  const [visibility, setVisibility] = useState('public');
  const [selectedOption, setSelectedOption] = useState('Plain');

  const options = ['Plain', 'Markdown', 'Image'];
  const [title, setTitle] = useState('');
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
      title: title || 'New Post',
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
      await createPost(authorId, postData);
      navigate('/');
    } catch (error) {
      // TODO: Handle error
    }
  };

  const handleDeleteClick = async () => {
    try {
      const response = await deletePost(authorId, postId);

      if (!response.status === 204) {
        throw new Error('Failed to delete post.');
      }
      navigate('/');
    } catch (error) {
      // TODO: Handle error
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
        <h1>{postId ? 'Edit' : 'Create'} Post</h1>
        <div className={'posts-options'}>{options.map(renderOption)}</div>
      </div>

      {/* <textarea
        id="title-textarea"
        placeholder="Title"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
      ></textarea> */}
      <input
        type="text"
        id="title-input"
        placeholder="Title"
        value={title}
        onChange={(event) => setTitle(event.target.value)}
      ></input>

      {selectedOption === 'Image' ? (
        <div id="image-selection-container" onClick={handleImageUploaderClick}>
          {uploadedImage ? (
            <img
              src={uploadedImage}
              alt="Uploaded"
              className="uploaded-image"
            />
          ) : (
            <><ImageUploader
              className="image-uploader-svg"
            />
          <p id="image-selection-hint">Click to upload an image</p></>
          )}
          <input
            type="file"
            ref={fileInputUpload}
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
        </div>
      ) : selectedOption === 'Plain' ? (
        <textarea
          id="plain-textarea"
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
        {postId && (
          <button className="delete-button" onClick={handleDeleteClick}>
            Delete
          </button>
        )}
      </div>
    </div>
  );
};

export default Post;
