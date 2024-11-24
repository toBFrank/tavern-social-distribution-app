import './styles/App.css';
import NavigationBar from './components/NavigationBar';
import AppRoutes from './routes/AppRoutes';
import Cookies from 'js-cookie';
import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

function App() {
  const location = useLocation();
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
    // console.log(`Navbar is now ${newExpanded ? 'expanded' : 'minimized'}`);
  };

  // No margin and padding in Login and Signup page
  const isLoginPage = location.pathname === '/login';
  const isSignupPage = location.pathname === '/signup';

  const style = {
    marginLeft: isLoginPage || isSignupPage ? 0 : expanded ? 320 : 170,
    padding: isLoginPage || isSignupPage ? 0 : undefined,
    backgroundColor: isSignupPage ? '#C8BE8A' : undefined, // Background for signup page
  };

  return (
    <div className="App" style={style}>
      {authorIdExists && !isLoginPage && !isSignupPage && (
        <NavigationBar
          expanded={expanded}
          onToggleExpanded={handleToggleExpanded}
        />
      )}
      <AppRoutes />
    </div>
  );
}

export default App;

