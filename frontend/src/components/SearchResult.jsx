// https://github.com/CodeCompleteYT/react-search-bar/blob/main/src/components/SearchResult.jsx search result 2024-10-18, author: CodeCompleteYT 

import "../styles/components/SearchResult.css";
import { useNavigate } from "react-router-dom";

const SearchResult = ({ result }) => {
  const navigate = useNavigate();

  const handleClickProfile = async () => {
    console.log(result);
    const authorId = result.id.split('/').slice(-2, -1)[0]; // Grabs the second last segment, which is the UUID
    navigate(`/profile/${authorId}`);
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