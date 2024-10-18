import './styles/App.css';
import NavigationBar from './components/NavigationBar';
import AppRoutes from './routes/AppRoutes';
import { useAuth } from './contexts/AuthContext';
import { useEffect } from 'react';
import api from './services/axios';

function App() {
  const { userAuthentication } = useAuth();

  useEffect(() => {
    if (userAuthentication.token) {
      api.defaults.headers.common['Authorization'] =
        `Token ${userAuthentication.token}`;
    } else {
      delete api.defaults.headers.common['Authorization'];
    }
  }, [userAuthentication]);

  return (
    <div className="App">
      <NavigationBar />
      <AppRoutes />
    </div>
  );
}

export default App;
