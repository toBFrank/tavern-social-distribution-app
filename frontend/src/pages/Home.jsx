import React, { useState, useEffect } from 'react';

import '../styles/pages/Home.css';
import FollowRequests from '../components/FollowRequests';
import SearchBar from '../components/SearchBar';
import SearchResultsList from '../components/SearchResultsList';
import { makeGithubActivityPosts } from '../services/GithubService';

const Home = () => {
  const [results, setResults] = useState([]);

  useEffect(() => {
    makeGithubActivityPosts();
  });

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
