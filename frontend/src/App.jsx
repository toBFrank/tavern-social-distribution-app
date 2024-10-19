import './styles/App.css';
import NavigationBar from './components/NavigationBar';
import AppRoutes from './routes/AppRoutes';
import { useAuth } from './contexts/AuthContext';
import { useEffect } from 'react';
import api from './services/axios';
import { useLocation } from 'react-router-dom';

function App() {
  const { userAuthentication } = useAuth();
  const location = useLocation(); // Get the current location

  useEffect(() => {
    // Define routes that do not require authentication
    const publicRoutes = ['/login', '/signup'];

    // Check if the current route is a public route
    if (!publicRoutes.includes(location.pathname) && userAuthentication.token) {
      // Set the Authorization header for all routes except login and signup
      api.defaults.headers.common['Authorization'] = `Token ${userAuthentication.token}`;
    } else {
      // Remove the Authorization header for login and signup
      delete api.defaults.headers.common['Authorization'];
    }
  }, [userAuthentication, location.pathname]); // Dependency on location.pathname

  return (
    <div className="App">
      <NavigationBar />
      <AppRoutes />
    </div>
  );
}

export default App;
