import './styles/App.css';
import NavigationBar from './components/NavigationBar';
import AppRoutes from './routes/AppRoutes';
import { useLocation } from 'react-router-dom';

function App() {
  const location = useLocation(); // Get the current location

  return (
    <div className="App">
      <NavigationBar />
      <AppRoutes />
    </div>
  );
}

export default App;
