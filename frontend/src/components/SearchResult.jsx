// https://github.com/CodeCompleteYT/react-search-bar/blob/main/src/components/SearchResult.jsx search result 2024-10-18, author: CodeCompleteYT 

import "../styles/components/SearchResult.css";

const SearchResult = ({ result }) => {
  return (
    <div
      className="search-result"
      onClick={(e) => alert(`You selected ${result}!`)}
    >
      {result}
    </div>
  );
};

export default SearchResult;