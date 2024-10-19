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
        const data = await response.json(); // Parse JSON response
        setPosts(data); // Set the state with fetched posts
      } catch (error) {
        setError(error.message); // Set error if fetching fails
      } finally {
        setLoading(false); // Set loading to false after request is complete
      }
    };

    fetchPublicPosts();
  }, []);

  const handleFilterClick = (filter) => {
    setSelectedFilter(filter); // Set the selected filter based on user click
  };

  // Sort posts by most recent date
  const filteredPosts = posts.slice().sort((a, b) => new Date(b.published) - new Date(a.published));

  if (loading) {
    return <p>Loading...</p>; // Will show while the page is loading
  }

  if (error) {
    return <p>Error: {error}</p>; // Display error message
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
          {/* Sorted Public Posts Section */}
          {filteredPosts.length > 0 ? (
            filteredPosts.map((post) => (
              <div key={post.id} className="post">
                <div className="post-header">
                  <img
                    src={post.profileImage} // Assuming each post contains profileImage
                    alt={post.displayName}
                    className="post-avatar"
                  />
                  <div>
                    <h3>{post.displayName}</h3> {/* Author's display name */}
                    <p>{new Date(post.published).toLocaleString()}</p> {/* Post published date */}
                  </div>
                </div>
                <div className="post-content">
                  <p>{post.text_content}</p> {/* Post content */}
                </div>
              </div>
            ))
          ) : (
            <p>No public posts available.</p> // No posts found
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;
