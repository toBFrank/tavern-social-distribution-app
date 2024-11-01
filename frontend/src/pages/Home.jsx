import React, { useState, useEffect, useRef } from 'react';
import '../styles/pages/Home.css';
import FollowRequests from '../components/FollowRequests';
import SearchBar from '../components/SearchBar';
import SearchResultsList from '../components/SearchResultsList';
import { makeGithubActivityPosts } from '../services/GithubService';
import Cookies from 'js-cookie';
import { getAuthorProfile } from '../services/profileService';
import api from '../services/axios'; 
import PostBox from '../components/PostBox';

const Home = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState('Posts');
  const [authorProfiles, setAuthorProfiles] = useState({});
  const [results, setResults] = useState([]);
  const [authorizedAuthors, setAuthorizedAuthors] = useState([]); 
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
        const response = await api.get('posts/');
        const data = response.data;
        
        setPosts(data.posts);
        setAuthorizedAuthors(data.authorized_authors_per_post);

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
    const isAuthorized = postAuthorization?.authorized_authors.includes(
      post.author_id
    );
    if (!isAuthorized) {
      return false; 
    }

    // Check visibility based on selected filter
    if (selectedFilter === 'Public') {
      return post.visibility === 'PUBLIC';
    } else if (selectedFilter === 'Unlisted') {
      return post.visibility === 'UNLISTED' || post.visibility === 'SHARED'; // CHANGE: Should only show to those who are following the user!;
    } else if (selectedFilter === 'Friends') {
      return post.visibility === 'FRIENDS';
    }
    return true;
  });

  return (
    <div className="home-page-container">
      <div className="home-container">
        <h1>Feeds</h1>
        <SearchBar setResults={setResults} />
        {results.length > 0 && <SearchResultsList results={results} />}
        <div className="home-filter-options">
          <h3
            onClick={() => handleFilterClick('Posts')}
            style={{
              opacity: selectedFilter === 'Posts' ? '100%' : '50%',
              cursor: 'pointer',
            }}
          >
            Posts
          </h3>
          <h3
            onClick={() => handleFilterClick("Friend's Posts")}
            style={{
              opacity: selectedFilter === "Friend's Posts" ? '100%' : '50%',
              cursor: 'pointer',
            }}
          >
            Friend's Posts
          </h3>
        </div>
        <div className="posts-container">
          {filteredPosts.length > 0 ? (
            <ul>
              {filteredPosts.map((post) => {
                const postAuthorization = authorizedAuthors.find(
                  (auth) => auth.post_id === post.id
                );
                const authorizedAuthorsForPost = postAuthorization?.authorized_authors || [];
                return (
                  <li key={post.id}>
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
