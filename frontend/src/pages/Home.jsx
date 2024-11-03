import React, { useState, useEffect, useRef } from 'react';
import '../styles/pages/Home.css';
import FollowRequests from '../components/FollowRequests';
import SearchBar from '../components/SearchBar';
import SearchResultsList from '../components/SearchResultsList';
import { makeGithubActivityPosts } from '../services/GithubService';
import Cookies from 'js-cookie';
import { getAuthorProfile } from '../services/profileService';
import { checkIfFollowing } from '../services/FollowService'; 
import api from '../services/axios'; 
import PostBox from '../components/PostBox';

const Home = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState('Public');
  const [authorProfiles, setAuthorProfiles] = useState({});
  const [results, setResults] = useState([]);
  const [authorizedAuthors, setAuthorizedAuthors] = useState([]); 
  const [followingStatus, setFollowingStatus] = useState({});
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) {
      return;
    }
    hasRun.current = true;
    const makeGithubActivityPostsFromService = async () => {
      const authorId = Cookies.get('author_id');
      if (!authorId) {
        return;
      }
      await makeGithubActivityPosts(authorId);
    };

    makeGithubActivityPostsFromService();
  }, []);

  const handleFilterClick = (filter) => {
    setSelectedFilter(filter);
  };

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await api.get('posts/'); // Using axios instance to fetch posts
        const data = response.data; // Accessing data directly from the response

        // Set posts directly from the response structure
        setPosts(data.posts);

        // Set authorized authors
        setAuthorizedAuthors(data.authorized_authors_per_post); // Set authorized authors data

        // Fetch author profiles based on the retrieved posts
        const profiles = await Promise.all(
          data.posts.map(async (post) => {
            try {
              const profile = await getAuthorProfile(post.author_id);
              return {
                authorId: post.author_id,
                displayName: profile.displayName,
                profileImage: profile.profileImage,
              };
            } catch (profileError) {
              console.error(
                `Error fetching profile for author ${post.author_id}:`,
                profileError
              );
              return {
                authorId: post.author_id,
                displayName: null,
                profileImage: null,
              };
            }
          })
        );

        const profileMap = profiles.reduce(
          (acc, { authorId, displayName, profileImage }) => {
            acc[authorId] = { displayName, profileImage };
            return acc;
          },
          {}
        );
        setAuthorProfiles(profileMap);

        const currentUserId = Cookies.get('author_id');
        const followingPromises = data.posts.map(post =>
          checkIfFollowing(post.author_id, currentUserId)
        );

        const followingResponses = await Promise.all(followingPromises);
        const followingStatusMap = {};

        followingResponses.forEach((response, index) => {
          if (response && response.data) {
            followingStatusMap[data.posts[index].author_id] = response.data.status === "Following";
          }
        });

        setFollowingStatus(followingStatusMap); 

      } catch (err) {
        console.error('Fetch Error:', err.message);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  if (loading) {
    return <p>Loading...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  // Filter posts based on visibility and selected filter
  const filteredPosts = posts.filter((post) => {    
    // Find the corresponding entry in authorizedAuthors for the current post
    const postAuthorization = authorizedAuthors.find(
      (auth) => auth.post_id === post.id
    );

    // If this post is public, it should be displayed to everyone
    if (post.visibility === 'PUBLIC' && selectedFilter === 'Public') {
      return true; // Public posts should always be included
    }
    const currentUserId = Cookies.get('author_id');
    const isAuthorized = postAuthorization?.authorized_authors.includes(
      currentUserId
    );

    if (!isAuthorized) {
      return false; // Skip unauthorized posts
    }

    // Check visibility based on selected filter
    if (selectedFilter === 'Public') {
      return post.visibility === 'PUBLIC';
    } else if (selectedFilter === 'Unlisted') {
      if (post.visibility === 'UNLISTED') {
        return  followingStatus[post.author_id];
       }
    if (post.visibility === 'SHARED') {
      return followingStatus[post.author_id]; // Show shared posts of people the current user follows
    }
    return false; 
    } else if (selectedFilter === 'Friends') {
        console.log(1);
        console.log(post.visibility === 'FRIENDS');
        return post.visibility === 'FRIENDS';
    }
    return true; // Fallback case, should return all posts if no filter is selected
  });

  return ( 
    <div className="home-page-container">
      <div className="home-container">
        <h1>Feeds</h1>
        <SearchBar setResults={setResults} />
        {results.length > 0 && <SearchResultsList results={results} />}
        <div className="home-filter-options">
          <h3
            onClick={() => handleFilterClick('Public')}
            style={{
              opacity: selectedFilter === 'Public' ? '100%' : '50%',
              cursor: 'pointer',
            }}
          >
            Public
          </h3>
          <h3
            onClick={() => handleFilterClick('Friends')}
            style={{
              opacity: selectedFilter === 'Friends' ? '100%' : '50%',
              cursor: 'pointer',
            }}
          >
            Friends
          </h3>
          <h3
            onClick={() => handleFilterClick('Unlisted')}
            style={{
              opacity: selectedFilter === 'Unlisted' ? '100%' : '50%',
              cursor: 'pointer',
            }}
          >
            Unlisted
          </h3>
        </div>
        <div className="posts-container">
          {filteredPosts.length > 0 ? (
            <ul>
              {filteredPosts.map((post) => {
                // Find authorized authors for the post
                const postAuthorization = authorizedAuthors.find(
                  (auth) => auth.post_id === post.id
                );
                const authorizedAuthorsForPost = postAuthorization?.authorized_authors || [];
                return (
                  <li key={post.id}>
                    {/* Temporarily removed the Link component */}
                    <div>
                      <PostBox post={post} poster={authorProfiles[post.author_id]} />
                    </div>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p>No posts available.</p>
          )}
        </div>
      </div>
      <div className="follow-request-container">
        <FollowRequests />
      </div>
    </div>
  );
};

export default Home;
