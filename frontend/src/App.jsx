import './styles/App.css';
import NavigationBar from './components/NavigationBar';
import AppRoutes from './routes/AppRoutes';
import Cookie from 'js-cookie';
import { useState, useEffect } from 'react';

function App() {
  const [authorIdExists, setAuthorIdExists] = useState(
    !!Cookie.get('author_id')
  );

  useEffect(() => {
    const checkCookie = () => {
      setAuthorIdExists(!!Cookie.get('author_id'));
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

  return (
    <div className="App">
      {authorIdExists && <NavigationBar />}
      <AppRoutes />
    </div>
  );
}

export default App;
