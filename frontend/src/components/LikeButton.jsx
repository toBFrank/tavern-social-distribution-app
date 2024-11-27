// https://codepen.io/bnewton/pen/KMbLZx
import React, { useEffect, useState, useRef } from 'react';
import Cookies from 'js-cookie';
import { createLike, getLikes } from '../services/LikesService';
import { Favorite } from '@mui/icons-material';
import mojs from '@mojs/core';
import '../styles/components/LikeButton.css';
import { getAuthor } from '../services/AuthorsService';
import { Author } from '../models/Author';
import AuthorsListModal from '../components/AuthorsListModal';

const LikeButton = ({ post, posterId }) => {
  const [likesCount, setLikesCount] = useState(0);
  const [showAuthorsModal, setShowAuthorsModal] = useState(false);
  const [authorsList, setAuthorsList] = useState([]);
  const [isLiked, setIsLiked] = useState(false);
  const authorId = Cookies.get('author_id');
  const [currentProfileData, setCurrentProfileData] = useState(null);
  const buttonRef = useRef(null); // Reference for the button element

  // Initialize animation
  useEffect(() => {
    const el = buttonRef.current;

    const scaleCurve = mojs.easing.path('M0,100 L25,99.9999983 C26.2328835,75.0708847 19.7847843,0 100,0');

    const burst1 = new mojs.Burst({
      parent: el,
      radius: { 0: 100 },
      angle: { 0: 45 },
      y: -10,
      count: 10,
      children: {
        shape: 'circle',
        radius: 30,
        fill: ['red', 'white'],
        strokeWidth: 15,
        duration: 500,
      },
    });

    const scaleAnimation = new mojs.Tween({
      duration: 900,
      onUpdate: (progress) => {
        const scaleProgress = scaleCurve(progress);
        el.style.transform = `scale3d(${scaleProgress}, ${scaleProgress}, 1)`;
      },
    });

    const burst2 = new mojs.Burst({
      parent: el,
      radius: { 0: 125 },
      angle: { 0: -45 },
      y: -10,
      count: 10,
      children: {
        shape: 'circle',
        radius: 30,
        fill: ['white', 'red'],
        strokeWidth: 15,
        duration: 400,
      },
    });

    const timeline = new mojs.Timeline();
    timeline.add(burst1, scaleAnimation, burst2);

    // Attach animation to the button click
    const animate = () => {
      if (!isLiked) {
        timeline.play();
      }
    };

    el.addEventListener('click', animate);

    return () => {
      el.removeEventListener('click', animate); // Cleanup event listener
    };
  }, [isLiked]);

  // Fetch likes when component mounts
  useEffect(() => {
    const fetchLikes = async () => {
      try {
        const likesResponse = await getLikes(authorId, post.id);
        setLikesCount(likesResponse.count);

        const userLike = likesResponse.src.find((like) => {
          const authorUuid = like.author.id.split('authors/')[1].replace('/', '');
          return authorUuid === authorId;
        });

        if (userLike) setIsLiked(true);
      } catch (error) {
        console.error(error);
      }
    };

    fetchLikes();
  }, [authorId, post.id]);

  useEffect(() => {
    getAuthor(authorId)
      .then((data) => {
        setCurrentProfileData(data);
      })
      .catch((error) => {
        console.error(error);
      });
  }, []);

  const handleLike = async () => {
    if (!isLiked) {
      const currentHost = window.location.origin;
      const likeData = {
        type: 'like',
        author: currentProfileData,
        object: `${post.author.id}posts/${post.id}/`,
      };

      try {
        const response = await createLike(authorId, likeData);
        if (response.status === 201) {
          setLikesCount((prev) => prev + 1);
          setIsLiked(true);
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
      const likesResponse = await getLikes(authorId, postId);

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
  };

  return (
    <div className="like-button-container">
      <button
        className={`like-button ${isLiked ? 'active' : ''}`}
        onClick={handleLike}
        ref={buttonRef}
      >
        <Favorite className={`like-heart ${isLiked ? 'liked' : 'not-liked'}`} />
      </button>
      <span className="like-text" onClick={handleShowAuthors}>
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