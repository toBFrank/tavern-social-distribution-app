import React, { useEffect, useState } from 'react';
import '../styles/pages/Home.css';
import FollowRequests from '../components/FollowRequests';

const Home = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState('Public');

  useEffect(() => {
    const fetchPublicPosts = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/posts/');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json(); 
        setPosts(data);  
      } catch (error) {
        setError(error.message);  
      } finally {
        setLoading(false);  
      }
    };

    fetchPublicPosts();
  }, []);

  const handleFilterClick = (filter) => {
    setSelectedFilter(filter); 
  };

  if (loading) {
    return <p>Loading...</p>;  // Will show while the page is loading
  }

  if (error) {
    return <p>Error: {error}</p>;  // Display error message
  }

  return (
    <div className='home-page-container'>
      <FollowRequests />
      <div className='home-container'>
          <div className='home-texts'>
            <h1>Feeds</h1>
            <div className='home-filter-options'>
              <h3
                onClick={() => handleFilterClick('Public')}
                style={{
                  opacity: selectedFilter === 'Public' ? '100%' : '50%',
                  cursor: 'pointer',
                }}
              >
                Public
              </h3>
              <h3
                onClick={() => handleFilterClick('Following')}
                style={{
                  opacity: selectedFilter === 'Following' ? '100%' : '50%',
                  cursor: 'pointer',
                }}
              >
                Following
              </h3>
          </div>
        </div>
        <div className='posts-container'>
          <div className='posts-list'>
            {posts.length > 0 ? (
              <ul>
                {posts.map((post) => (
                  <li key={post.author_id}> {/* To do: Change this to author name!*/}
                    <h3>{post.id}</h3>
                    <h4>{post.title}</h4>
                    <p>{post.text_content}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No public posts available.</p>  // No posts found
            )}
          </div>
        </div>
      </div>
      
      
    </div>
  );
};

export default Home;
