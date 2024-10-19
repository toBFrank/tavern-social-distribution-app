// https://github.com/CodeCompleteYT/react-search-bar/blob/main/src/components/SearchResultsList.jsx search results list 2024-10-18, author: CodeCompleteYT 

import "../styles/components/SearchResultsList.css";
import SearchResult from "./SearchResult";

const SearchResultsList = ({ results }) => {
  return (
    <div className="results-list">
      {results.map((result, id) => {
        return <SearchResult result={result.displayName} key={id} />;
      })}
    </div>
  );
};

export default SearchResultsList;