// https://github.com/CodeCompleteYT/react-search-bar/blob/main/src/components/SearchBar.jsx search bar logic 2024-10-18, author: CodeCompleteYT from youtube tutorial https://www.youtube.com/watch?v=sWVgMcz8Q44
 

import { useState } from "react";
import { Search } from "@mui/icons-material";
import { getAuthors } from '../services/AuthorsService';

import "../styles/components/SearchBar.css";

const SearchBar = ({ setResults }) => {
  const [input, setInput] = useState("");

  //TODO: ONLY RETURN AUTHORS THAT ARENT THE AUTHOR SEARCHING IT UP
  const fetchData = async (value) => {
    try {
      const authorsData = await getAuthors();
      const authorsArray = authorsData.authors;

      if (Array.isArray(authorsArray)) {
        const results = authorsArray.filter((author) => {
            return (
              value && //check that they've entered value into search bar --> if value is empy --> wont render anything
              author && //check that user exists
              author.displayName && //check that user has a display name
              author.displayName.toLowerCase().includes(value) //check if lowercase of authors name includes value entered into search bar
            );
          });
          
          setResults(results);
      } else {
        console.error("Expected authors to be an array, but got:", authorsArray);
      }
    } catch (error) {
      console.error('Error fetching authors:', error); 
    }
    
  };

  const handleChange = (value) => {
    setInput(value);
    fetchData(value);
  };

  return (
    <div className="input-wrapper">
      <Search id="search-icon" />
      <input
        placeholder="Search for authors..."
        value={input}
        onChange={(e) => handleChange(e.target.value)} // whenever change is made to text, the fetch is called
      />
    </div>
  );
};

export default SearchBar;
