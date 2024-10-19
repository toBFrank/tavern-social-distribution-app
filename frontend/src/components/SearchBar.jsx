// https://github.com/CodeCompleteYT/react-search-bar/blob/main/src/components/SearchBar.jsx search bar logic 2024-10-18, author: CodeCompleteYT
 

import { useState } from "react";
import { Search } from "@mui/icons-material";

import "../styles/components/SearchBar.css";

const SearchBar = ({ setResults }) => {
  const [input, setInput] = useState("");
  const token = '7e31046a8413002b920bdc8dd0232bad6c482e1e';

  //TODO: ONLY RETURN AUTHORS THAT ARENT THE AUTHOR SEARCHING IT UP
  const fetchData = (value) => {
    fetch("http://localhost:8000/api/authors/", {
        method: 'GET',
        headers: {
            'Authorization': `Token ${token}`, 
            'Content-Type': 'application/json',
        },
    }) //fetch is asynchronous and returns a result later on, need to call then to await for result to perform actions on it
    .then((response) => response.json())
    .then((json) => {
        const authorsArray = json.authors; // need to get authors

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
        }
        else {
            console.error("Expected authors to be an array, but got:", authorsArray);
        }
    })};

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
