// https://github.com/CodeCompleteYT/react-search-bar/blob/main/src/components/SearchBar.jsx search bar logic 2024-10-18, author: CodeCompleteYT
 

import { useState } from "react";
import { Search } from "@mui/icons-material";

import "../styles/components/SearchBar.css";

const SearchBar = ({ setResults }) => {
  const [input, setInput] = useState("");

  const fetchData = (value) => {
    fetch("https://jsonplaceholder.typicode.com/users") //fetch is asynchronous and returns a result later on, need to call then to await for result to perform actions on it
      .then((response) => response.json())
      .then((json) => {
        const results = json.filter((user) => {
          return (
            value &&
            user &&
            user.name &&
            user.name.toLowerCase().includes(value)
          );
        });
        setResults(results);
      });
  };

  const handleChange = (value) => {
    setInput(value);
    fetchData(value);
  };

  return (
    <div className="input-wrapper">
      <Search id="search-icon" />
      <input
        placeholder="Type to search..."
        value={input}
        onChange={(e) => handleChange(e.target.value)} // whenever change is made to text, the fetch is called
      />
    </div>
  );
};

export default SearchBar;
