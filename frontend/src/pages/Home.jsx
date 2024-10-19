import React, { useState } from 'react';

import "../styles/pages/Home.css"
import FollowRequests from '../components/FollowRequests';
import SearchBar from "../components/SearchBar";
import SearchResultsList from "../components/SearchResultsList";

const Home = () => {
  const [results, setResults] = useState([]);

  return (
    <div className="home-container">
      <div className="main-container">
        <SearchBar setResults={setResults} />
        {results && results.length > 0 && <SearchResultsList results={results} />}
        <h1>Home</h1>
      </div>
      <div className='follow-request-container'>
        <FollowRequests />
      </div>
    </div>
  );
};

export default Home;
