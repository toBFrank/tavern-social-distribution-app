//https://medium.com/@yuvidexter/%EF%B8%8Fadding-a-magical-like-button-to-your-react-js-464989211940 for like button jsx logic, Author: Yuvi Dexter, obtained 2024-10-19
import React, { useEffect, useState } from 'react';
import Cookies from 'js-cookie';
import { createLike, getLikes } from '../services/LikesService';
import { Favorite } from '@mui/icons-material';
import { getAuthorProfile } from '../services/profileService';
import '../styles/components/LikeButton.css';
import { Author } from '../models/Author';
import AuthorsListModal from '../components/AuthorsListModal';

const LikeButton = ({ postId }) => {
  const [likesCount, setLikesCount] = useState(0);
  const [showAuthorsModal, setShowAuthorsModal] = useState(false);
  const [authorsList, setAuthorsList] = useState([]);
  const [isLiked, setIsLiked] = useState(false);
  const authorId = Cookies.get('author_id');
  const [currentProfileData, setCurrentProfileData] = useState(null);

  //get likes w/ useEffect to update whenever postId changes or page reloads
  useEffect(() => {
    const fetchLikes = async () => {
      try {
        const likesResponse = await getLikes(authorId, postId);
        console.log(likesResponse);
        setLikesCount(likesResponse.count);

        //check if user liked post already
        const userLike = likesResponse.src.find((like) => {
          const authorUuid = like.author.id.split("authors/")[1].replace("/", "");
          return authorUuid === authorId
        }); //authors who liked post

        if (userLike) {
          setIsLiked(true);
        }
      } catch (error) {
        console.error(error);
      }
    };

    fetchLikes();
  }, [authorId, postId]);

  useEffect(() => {
    getAuthorProfile(authorId)
      .then((data) => {
        setCurrentProfileData(data);
      })
      .catch((error) => {
        console.error(error);
      });
  }, []); //empty dependency list so that its only called once to get author info when component mounts

  const handleLike = async () => {
    if (!isLiked) {
      //create like object
      const currentHost = window.location.origin; //getting host for post url
      const likeData = {
        type: 'like',
        author: currentProfileData,
        object: `${currentHost}/api/authors/${authorId}/posts/${postId}/`,
      };

      try {
        const response = await createLike(authorId, likeData);
        console.log(response.data);

        // only updating likes if request is successful
        if (response.status === 201) {
          setLikesCount(likesCount + 1);
          setIsLiked(true);
        } else if (response.status === 200) {
          console.log(response.data);
        } else {
          console.error('Creating like failed with ', response.status);
        }
      } catch (error) {
        console.error('Error handling like', error);
      }
    }
  };

  const handleShowAuthors = async () => {
    try {
      const likesResponse = await getLikes(authorId, postId) //hitting endpoint again because if you like, you'll have to call getLikes anyways
      console.log(likesResponse);

      // store authors who liked the post
      const authors = likesResponse.src.map(
        (like) =>
          new Author(
            like.author.id,
            like.author.host,
            like.author.displayName,
            like.author.github,
            like.author.profileImage,
            like.author.page
          )
      );
      setAuthorsList(authors);
      setShowAuthorsModal(true);
    } catch (error) {
      console.error(error);
    }
  }

  return (
    <div className="like-button-container">
      <button className="like-button" onClick={handleLike}>
        {isLiked ? (
          <Favorite className="like-heart" id="liked" />
        ) : (
          <Favorite className="like-heart" id="not-liked" />
        )}
      </button>
      <span className="like-text" onClick={handleShowAuthors}>
        {' '}
        {likesCount} {likesCount === 1 ? 'like' : 'likes'}
      </span>
      {showAuthorsModal && (
        <AuthorsListModal 
          authors={authorsList}
          onModalClose={() => setShowAuthorsModal(false)}
           />
      )}
    </div>
  );
};

export default LikeButton;
