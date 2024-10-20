//https://medium.com/@yuvidexter/%EF%B8%8Fadding-a-magical-like-button-to-your-react-js-464989211940 for like button jsx logic, Author: Yuvi Dexter, obtained 2024-10-19
import React, { useEffect, useState } from 'react';
import "../styles/components/LikeButton.css";
import Cookies from 'js-cookie';
import { createLike, getLikes } from '../services/LikesService';
import { Favorite } from "@mui/icons-material";

const LikeButton = () => {
  const [likes, setLikes] = useState(0);
  const [isLiked, setIsLiked] = useState(false);
  const authorId = Cookies.get('author_id');

  //get likes w/ useEffect to update whenever postId changes or page reloads
  useEffect(() => {
    const fetchLikes = async () => {
        try {
            const likesResponse = await getLikes(authorId, "23b10051-0059-410b-8685-0e558c6ddde5");
            setLikes(likesResponse.length);
            console.log(likesResponse);

            //check if user liked post already
            const userLike = likesResponse.find(like => like.author_id === authorId);
            if (userLike) {
                setIsLiked(true);
            }
        }
        catch(error) {
            console.error(error);
        }
    };

    fetchLikes();
  }, [authorId]);

  const handleLike = async () => {
    if (!isLiked) {
        //create like object
        const likeData = {
            type: "like",
            author: {
              type: "author",
              id: "http://nodeaaaa/api/authors/111",
              page: "http://nodeaaaa/authors/greg",
              host: "http://nodeaaaa/api/",
              displayName: "Greg Johnson",
              github: "http://github.com/gjohnson",
              profileImage: "https://i.imgur.com/k7XVwpB.jpeg",
            },
            published: new Date().toISOString(),
            id: "http://nodeaaaa/api/authors/111/liked/166",
            object: "http://localhost:8000/authors/222/posts/23b10051-0059-410b-8685-0e558c6ddde5",
        };

        try {
            const response = await createLike(authorId, likeData);

            // only updating likes if request is successful
            if (response.status === 201) {
                setLikes(likes + 1);
                setIsLiked(true);
            } else {
            console.error('Creating like failed with ', response.status);
            }
        } catch (error) {
            console.error('Error handling like', error);
        }
    }
  };

  return (
    <div>
      <button className='like-button' onClick={handleLike}>
        {isLiked ? <Favorite className='like-heart' id='liked'/> : <Favorite className='like-heart' id='not-liked'/>}
      </button>
      <span className='like-text'> {likes} {likes === 1 ? 'like' : 'likes'}</span>
    </div>
  );
};

export default LikeButton;