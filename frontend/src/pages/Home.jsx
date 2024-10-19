import React, { useState } from 'react';

import FollowRequests from '../components/FollowRequests';
import SearchBar from "../components/SearchBar";
import SearchResultsList from "../components/SearchResultsList";

const Home = () => {
  const [results, setResults] = useState([]);

  return (
    <div>
      <h1>Home</h1>
      <FollowRequests />
      <div className="search-bar-container">
        <SearchBar setResults={setResults} />
        {results && results.length > 0 && <SearchResultsList results={results} />}
      </div>
    </div>
  );
};

export default Home;
