// https://github.com/CodeCompleteYT/react-search-bar/blob/main/src/components/SearchBar.jsx search bar logic 2024-10-18, author: CodeCompleteYT from youtube tutorial https://www.youtube.com/watch?v=sWVgMcz8Q44

import { useState } from 'react';
import { Search } from '@mui/icons-material';
import { getRemoteAuthors } from '../services/AuthorsService';

import '../styles/components/SearchBar.css';

const SearchBar = ({ setResults }) => {
  const [input, setInput] = useState('');
  const [authors, setAuthors] = useState([]);  // State to store the list of authors
  const [isFocused, setIsFocused] = useState(false);

  //TODO: ONLY RETURN AUTHORS THAT ARENT THE AUTHOR SEARCHING IT UP
  const fetchData = async () => {
    try {
      const authorsArray = await getRemoteAuthors(); //call local endpoint to get remote authors as well as authors on this node

      if (Array.isArray(authorsArray)) {
        setAuthors(authorsArray);  // Store the authors in the state
      } else {
        console.error('Expected authors to be an array, but got:', authorsArray);
      }
    } catch (error) {
      console.error('Error fetching authors:', error);
    }

  };

  const handleChange = (value) => {
    setInput(value);

    const filteredResults = authors.filter((author) => {
      return (
        value && //check that they've entered value into search bar --> if value is empy --> wont render anything
        author && //check that user exists
        author.displayName && //check that user has a display name
        author.displayName.toLowerCase().includes(value.toLowerCase()) //check if lowercase of authors name includes value entered into search bar
      );
    });

    setResults(filteredResults);
  };

  const handleFocus = () => {
    if (!isFocused) {
      setIsFocused(true);
      fetchData();  // Fetch the authors once when focused
    }
  };

  return (
    <div className="input-wrapper">
      <Search id="search-icon" />
      <input
        id="search-input"
        placeholder="Search for authors..."
        value={input}
        onChange={(e) => handleChange(e.target.value)} // whenever change is made to text, the fetch is called
        onFocus={handleFocus}
      />
    </div>
  );
};

export default SearchBar;
