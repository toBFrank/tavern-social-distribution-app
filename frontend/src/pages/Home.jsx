import React, { useState, useEffect, useRef } from 'react';

import '../styles/pages/Home.css';
import FollowRequests from '../components/FollowRequests';
import SearchBar from '../components/SearchBar';
import SearchResultsList from '../components/SearchResultsList';
import { makeGithubActivityPosts } from '../services/GithubService';
import Cookies from 'js-cookie';

const Home = () => {
  const [results, setResults] = useState([]);
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
      await makeGithubActivityPosts('haileyok', authorId);
    };

    makeGithubActivityPostsFromService();
  }, []);

  return (
    <div className="home-container">
      <h1>Home</h1>
      <div className="main-container">
        <SearchBar setResults={setResults} />
        {results && results.length > 0 && (
          <SearchResultsList results={results} />
        )}
      </div>
      <div className="follow-request-container">
        <FollowRequests />
      </div>
    </div>
  );
};

export default Home;
