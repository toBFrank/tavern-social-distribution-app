import React, { useState, useRef, useEffect } from 'react';
import '../styles/pages/Post.css';
import { ReactComponent as ImageUploader } from './../assets/imageUploader.svg';
import MarkdownEditor from '../components/MarkdownEditor';
import { createPost, getPost, updatePost } from '../services/PostsService';
import Cookies from 'js-cookie';
import { useParams,useNavigate } from 'react-router-dom';

const Post = ( ) => {
  //#region Properties
  const authorId = Cookies.get('author_id');
  const { postId } = useParams(); 
  console.log('Post ID:', postId)

  const navigate = useNavigate();
  const [visibility, setVisibility] = useState('public');
  const [selectedOption, setSelectedOption] = useState('Plain');

  const options = ['Plain', 'Markdown', 'Image'];
  const [title, setTitle] = useState('');
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imgFile, setImgFile] = useState(null);
  const fileInputUpload = useRef(null);
  const [plainText, setPlainText] = useState('');
  const [markdown, setMarkdown] = useState('');
  const [loading, setLoading] = useState(true);

  //#endregion

  //#region Fetch Post Data (for editing)
  useEffect(() => {
    if (postId) {
      // If we're editing a post, fetch its data
      console.log('useEffect triggered for postId:', postId);
      getPost(authorId, postId)
        .then((response) => {
          const post = response.data;
          setTitle(post.title || '');
          if (post.content_type === 'text/markdown') {
            setMarkdown(post.text_content || '');  // Set the markdown content
            setSelectedOption('Markdown');  // Set the editor mode to Markdown
          } else {
            setPlainText(post.text_content || '');  // Set plain text content
            setSelectedOption('Plain');  // Set the editor mode to Plain
          }
          setVisibility(post.visibility.toLowerCase());
          setSelectedOption(post.image_content ? 'Image' : post.content_type === 'text/markdown' ? 'Markdown' : 'Plain');
          if (post.image_content) {
            setUploadedImage(`http://localhost:8000${post.image_content}`);
          }
          setLoading(false);
        })
        .catch((error) => {
          console.error('Error fetching post:', error);
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [postId, authorId]);
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
      setImgFile(file);
    }
  };
  const handlePlainTextChange = (event) => {
    setPlainText(event.target.value);
  };

  const handlePostClick = async () => {
    const postData = new FormData(); // Use FormData to handle file uploads

    // Add necessary fields to the FormData object
    postData.append('author_id', authorId);
    postData.append('title', title || 'New Post');
    postData.append(
      'text_content',
      selectedOption === 'Plain'
        ? plainText
        : selectedOption === 'Markdown'
          ? markdown
          : ''
    );
    postData.append(
      'content_type',
      selectedOption === 'Image'
        ? 'image'
        : selectedOption === 'Markdown'
          ? 'text/markdown'
          : 'text/plain'
    );
    postData.append('visibility', visibility.toUpperCase());

    // If an image file is selected, add it to the FormData
    if (selectedOption === 'Image' && imgFile) {
      postData.append('image_content', imgFile); // 'image_content' should match your Django model field name
    }

    try {
      if (postId) {
        // Update post if postId exists
        await updatePost(authorId, postId, postData);
      } else {
        // Create a new post if no postId
        await createPost(authorId, postData);
      }  
      navigate(`/profile/${authorId}`);
    } catch (error) {
      // TODO: Handle error
    }
  };

  const handleDeleteClick = async () => {
    try {
      // Change post visibility to 'DELETED'
      const authorId = Cookies.get('author_id');

      if (!authorId) {
        throw new Error('Author ID is missing.'); // Handle case where author_id is not available
      }
      const postData = { visibility: 'DELETED', author_id: authorId }; // Include author_id in the request
      const response = await updatePost(authorId, postId, postData); // Update the post's visibility

      if (response.status !== 200) {
        throw new Error('Failed to mark post as deleted.');
      }
      navigate('/');
    } catch (error) {
      console.error('Error deleting post:', error);
    }
  };
  //#endregion

  //#region Functions
  //#endregion

  if (loading) {
    return <p>Loading...</p>; // Display a loading state while the post data is being fetched
  }


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
            <>
              <ImageUploader className="image-uploader-svg" />
              <p id="image-selection-hint">Click to upload an image</p>
            </>
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