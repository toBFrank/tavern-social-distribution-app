// https://mui.com/material-ui/react-modal/ for 'Basic Modal' code from MUI, 2024-10-19

import React, { useState } from 'react';
import Box from '@mui/material/Box';
import { Comment } from "@mui/icons-material";
import Typography from '@mui/material/Typography';
import Modal from '@mui/material/Modal';
import "../styles/components/CommentsModal.css";
import Cookies from 'js-cookie';
import { getComments } from '../services/CommentsService';

const CommentsModal = ({ postId }) => {
    const authorId = Cookies.get('author_id');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [comments, setComments] = useState([]);
    console.log(postId);
    const handleOpen = async () => {
        setIsModalOpen(true);
        const fetchComments = await getComments(authorId, postId);
        console.log(fetchComments);
        setComments(fetchComments);
    };

    const handleClose = () => setIsModalOpen(false);
  
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
          </Box>
        </Modal>
      </>
    );
  };

export default CommentsModal;
