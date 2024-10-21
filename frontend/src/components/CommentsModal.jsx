// https://mui.com/material-ui/react-modal/ for 'Basic Modal' code from MUI to show comments, 2024-10-19
import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import { Comment } from "@mui/icons-material";
import Typography from '@mui/material/Typography';
import Modal from '@mui/material/Modal';
import "../styles/components/CommentsModal.css";
import Cookies from 'js-cookie';
import { getComments, createCommentLocal } from '../services/CommentsService';
import { getAuthorProfile } from '../services/profileService'; 

const CommentsModal = ({ postId }) => {
    const authorId = Cookies.get('author_id');
    const [currentProfileData, setCurrentProfileData] = useState(null); 
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');

    const handleOpen = async () => {
        setIsModalOpen(true);
        const fetchComments = await getComments(authorId, postId);
        setComments(fetchComments);
    };

    const handleClose = () => setIsModalOpen(false);

    const handleCommentSubmit = async () => {
        if (newComment.trim()) {
            const currentHost = window.location.origin; //getting host for post url
            const commentData = {
                type: 'comment',
                author: currentProfileData,
                comment: newComment,
                contentType: 'text/markdown',
                post: `${currentHost}/api/authors/${authorId}/posts/${postId}/`,
            }
            const response = await createCommentLocal(authorId, commentData);
            console.log(response);
            setComments([...comments, { comment: newComment }]);
            setNewComment(''); // Clear the input after posting the comment
        }
    };

    useEffect(() => {
        getAuthorProfile(authorId)
        .then((data) => {
            setCurrentProfileData(data);
        })
        .catch((error) => {
            console.error(error);
        })
    }, []) //empty dependency list so that its only called once to get author info when component mounts
  
    return (
      <>
        <button className="comments-button" onClick={handleOpen}>
          <Comment />
        </button>
        <Modal
          open={isModalOpen}
          onClose={handleClose}
          aria-labelledby="comments-modal-title"
          aria-describedby="comments-modal-description"
        >
          <Box className={"modalBox"}>
            <Typography id="comments-modal-title" variant="h6" component="h2">
              Comments
            </Typography>
            <Typography id="comments-modal-description" sx={{ mt: 2 }}>
              {comments.length > 0 ? (
                comments.map((comment, index) => (
                  <Typography key={index} variant="body1" sx={{ mt: 1 }}>
                    {comment.comment} 
                  </Typography>
                ))
              ) : (
                <Typography variant="body1">No comments available.</Typography>
              )}
            </Typography>
            <div className="comment-input-box">
              <textarea
                type="text"
                placeholder="Add a comment..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
              ></textarea>
              <button onClick={handleCommentSubmit}>Post</button>
            </div>
          </Box>
        </Modal>
      </>
    );
  };

export default CommentsModal;
