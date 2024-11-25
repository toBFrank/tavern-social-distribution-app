import React, { useState, useRef, useEffect } from 'react';
import '../styles/pages/Post.css';
import { ReactComponent as ImageUploader } from './../assets/imageUploader.svg';
import MarkdownEditor from '../components/MarkdownEditor';
import { createPost, getPost, updatePost } from '../services/PostsService';
import { getAuthor } from '../services/AuthorsService';
import Cookies from 'js-cookie';
import { useParams, useLocation, useNavigate } from 'react-router-dom';

const Post = () => {
  //#region Properties
  const authorId = Cookies.get('author_id');
  const { postId } = useParams();
  const navigate = useNavigate();
  const [visibility, setVisibility] = useState('public');
  const [selectedOption, setSelectedOption] = useState('Plain');
  const [profileData, setProfileData] = useState(null);

  const options = ['Plain', 'Markdown', 'Image'];
  const [title, setTitle] = useState('');
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imgFile, setImgFile] = useState(null);
  const fileInputUpload = useRef(null);
  const [plainText, setPlainText] = useState('');
  const [markdown, setMarkdown] = useState('');
  const [loading, setLoading] = useState(true);
  const [currentProfileData, setCurrentProfileData] = useState(null);

  // For sharing
  const location = useLocation();
  const sharePost = location.pathname.includes('/share');
  const sharedPostAuthor = location.state?.authorId;
  const currentHost = window.location.origin; // Get host for post URL

  useEffect(() => {
    if (!postId) {
      setUploadedImage(null);
    }
  }, [postId]);
  
  // Fetch current author profile on component mount
  useEffect(() => {
    getAuthor(authorId)
      .then((data) => {
        setCurrentProfileData(data);
      })
      .catch((error) => {
        console.error(error);
      });
  }, []); // Empty dependency list to run only once

  // Fetch the shared post author's profile data
  useEffect(() => {
    if (sharedPostAuthor) {
      getAuthor(sharedPostAuthor)
        .then((data) => {
          console.log('Author profile data:', data);
          setProfileData(data);
        })
        .catch((error) => {
          console.error('Error fetching author profile:', error);
        });
    }
  }, [sharedPostAuthor, sharePost]);

  //#endregion

  //#region Fetch Post Data (for editing)
  useEffect(() => {
    if (postId && !sharePost) {
      getPost(authorId, postId)
        .then((response) => {
          const post = response.data;
          setTitle(post.title || '');
          console.log('here', post)
          if (post.contentType === 'text/markdown') {
            setMarkdown(post.content || ''); // Set the markdown content
            setSelectedOption('Markdown'); // Set the editor mode to Markdown
          } else if ((post.contentType === 'text/plain')) {
            setPlainText(post.content || ''); // Set plain text content
            setSelectedOption('Plain'); // Set the editor mode to Plain
          } else {
            // console.log('Image!')
            if (post.contentType.startsWith('image/')) {
              setUploadedImage(post.contentType.includes('base64') ? post.content : `${currentHost}${post.content}`);
              setSelectedOption('Image');
            }
          }
          setVisibility(post.visibility.toLowerCase());
          setLoading(false);
        })
        .catch((error) => {
          console.error('Error fetching post:', error);
          setLoading(false);
        });
    } else if (sharePost) {
      getPost(sharedPostAuthor, postId)
        .then((response) => {
          const post = response.data;
          const displayName = profileData?.displayName || 'Unknown Author';
          const publishedDate = new Date(post.published).toLocaleString();

          setVisibility(post.visibility.toLowerCase());

          if (post.content_type.startsWith('image/')) {
            setSelectedOption('Image');
            // images are stored as base64 strings
            setUploadedImage(post.content);
            const creditsContent = `Author: ${displayName} (Published on: ${publishedDate}) \n\n Title: ${post.title || 'No Title Available'} \n\n${post.content || 'No Content Available'}`;
            setTitle(
              `Title: ${post.title || 'No Title Available'} \n\n ${creditsContent}`
            );
            // Fetch the image blob
            fetch(`${currentHost}${post.content}`)
              .then((response) => {
                if (response.ok) {
                  return response.blob();
                }
                throw new Error('Network response was not ok.');
              })
              .then((blob) => {
                const file = new File(
                  [blob],
                  post.content,
                  { type: blob.type }
                );
                setImgFile(file); // Set the imgFile state to the file object
              })
              .catch((error) => {
                console.error('Error fetching the image file:', error);
              });
          } else if (post.content_type === 'text/markdown') {
            const creditsContent = `Author: ${displayName} (Published on: ${publishedDate}) \n\n Title: ${post.title || 'No Title Available'} \n\n${post.content || 'No Content Available'}`;
            setMarkdown(creditsContent);
            setSelectedOption('Markdown');
          } else {
            const creditsContent = `Author: ${displayName} (Published on: ${publishedDate}) \n\n Title: ${post.title || 'No Title Available'} \n\n${post.content || 'No Content Available'}`;
            setPlainText(creditsContent);
            setSelectedOption('Image'); // Set the editor mode to Plain
          }

          setLoading(false); // Set loading to false after processing
        })
        .catch((error) => {
          console.error('Error sharing post:', error);
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [postId, authorId, sharePost, sharedPostAuthor, profileData?.displayName, currentHost]);
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
    console.log("handlePostClick triggered");
    const postData = {
      type: 'post',
      author: currentProfileData,
      title: title || 'New Post',
      visibility: visibility.toUpperCase(),
    };
    console.log("selectedOption: ", selectedOption)
    console.log("Uploaded file object:", imgFile);
    if (selectedOption === 'Plain') {
      postData.content = plainText;
      postData.contentType = 'text/plain';
    } else if (selectedOption === 'Markdown') {
      postData.content = markdown;
      postData.contentType = 'text/markdown';
    } else if (selectedOption === 'Image' && imgFile) {
      const base64Image = await imgToBase64(imgFile);
      postData.content = base64Image;
      //`${imgFile.type.split('/')[1]};base64`
      postData.contentType = imgFile.type;
      console.log("Uploaded file type:", imgFile.type);
    }

    try {
      if (sharePost) {
        // Create a new post when sharing
        await createPost(authorId, postData);
      } else if (postId) {
        const currentDateTime = new Date().toISOString();
        postData.published = currentDateTime;
        // Update post if postId exists
        await updatePost(authorId, postId, postData);
      } else {
        // Create a new post if no postId
        await createPost(authorId, postData);
      }
      navigate(`/profile/${authorId}`);
    } catch (error) {
      console.error('Error during post creation/updating:', error);
    }
  };

  const imgToBase64 = async (imgFile) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(imgFile);
      reader.onload = () => {
        const base64String = reader.result.split(',')[1];
        resolve(base64String);
      };
      reader.onerror = (error) => {
        reject(error);
      };
    });
  };

  const handleDeleteClick = async () => {
    try {
      // Change post visibility to 'DELETED'
      const authorId = Cookies.get('author_id');

      if (!authorId) {
        throw new Error('Author ID is missing.'); // Handle case where author_id is not available
      }
      const postData = { visibility: 'DELETED', author: authorId }; // Include author_id in the request
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
        <h1>{sharePost ? 'Share' : postId ? 'Edit' : 'Create'} Post</h1>
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
            readOnly={sharePost}
            disabled={sharePost}
          />
        </div>
      ) : selectedOption === 'Plain' ? (
        <textarea
          id="plain-textarea"
          placeholder="Type something here..."
          value={plainText}
          onChange={handlePlainTextChange}
          readOnly={sharePost}
          disabled={sharePost}
        ></textarea>
      ) : (
        <MarkdownEditor
          markdown={markdown}
          setMarkdown={setMarkdown}
          readOnly={sharePost}
          disabled={sharePost}
        />
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
