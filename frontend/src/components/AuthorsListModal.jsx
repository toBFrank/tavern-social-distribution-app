// https://mui.com/material-ui/react-modal/ for 'Basic Modal' code from MUI to show comments, 2024-10-31
// https://mui.com/material-ui/react-list/ for List of Avatars, sections 'Align list items' and 'Selected ListItem', 2024-10-31
import React, { useState } from 'react';
import Modal from '@mui/material/Modal';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import List from '@mui/material/List';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import { useNavigate } from 'react-router-dom';

const AuthorsListModal = ({ authors, onModalClose }) => { /* authors is the list of Author objects that should be displayed in modal*/
const navigate = useNavigate();

const handleClickProfile = async (author) => {
    navigate(`/profile/${author.id}`);
  }


return (
    <Modal 
        open={true} 
        onClose={onModalClose} 
        aria-labelledby="authors-list-title"
    >
        <Box className={'modalBox'}>
            <Typography id="authors-modal-title" variant="h6" component="h2">
            Authors
            </Typography>
            <List>
            {authors.map((author) => (
                <ListItemButton key={author.id} onClick={() => handleClickProfile(author)}>
                <ListItemAvatar>
                    <Avatar src={author.profileImage} alt={author.displayName}>
                    {author.displayName[0]} {/* Fallback for initials */}
                    </Avatar>
                </ListItemAvatar>
                <ListItemText
                    primary={author.displayName}
                    secondary={author.page ? `Page: ${author.page}` : ''}
                />
                </ListItemButton>
            ))}
            </List>
        </Box>
    </Modal>
)
};

export default AuthorsListModal;