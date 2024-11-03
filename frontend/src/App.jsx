import './styles/App.css';
import NavigationBar from './components/NavigationBar';
import AppRoutes from './routes/AppRoutes';
import Cookies from 'js-cookie';
import { useState, useEffect } from 'react';

function App() {
  // State for checking if the author ID cookie exists
  const [authorIdExists, setAuthorIdExists] = useState(
    !!Cookies.get('author_id')
  );

  // State to track if the navbar is expanded or minimized
  const [expanded, setExpanded] = useState(true); 

  useEffect(() => {
    const checkCookie = () => {
      setAuthorIdExists(!!Cookies.get('author_id'));
    };

    // Initial check
    checkCookie();

    // Set interval to check for changes every second (1000 ms)
    const intervalId = setInterval(checkCookie, 1000);

    // Cleanup function to clear the interval
    return () => {
      clearInterval(intervalId);
    };
  }, []);

  const handleToggleExpanded = (newExpanded) => {
    setExpanded(newExpanded);
    console.log(`Navbar is now ${newExpanded ? 'expanded' : 'minimized'}`); 
  };

  return (
    <div className="App" style={{ paddingLeft: expanded ? '15%' : '5%' }}>
      {authorIdExists && <NavigationBar expanded={expanded} onToggleExpanded={handleToggleExpanded} />}
      <AppRoutes />
    </div>
  );
}

export default App;
