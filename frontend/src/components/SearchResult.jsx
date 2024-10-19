// https://github.com/CodeCompleteYT/react-search-bar/blob/main/src/components/SearchResult.jsx search result 2024-10-18, author: CodeCompleteYT 

import "../styles/components/SearchResult.css";
import { useNavigate } from "react-router-dom";

const SearchResult = ({ result }) => {
  const navigate = useNavigate();

  const handleClickProfile = async () => {
    console.log(result);
    navigate(`/profile/${result.id}`);
  }

  return (
    <div
      className="search-result"
      onClick={handleClickProfile}
    >
      {result.displayName}
    </div>
  );
};

export default SearchResult;