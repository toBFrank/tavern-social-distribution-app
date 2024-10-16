import './styles/App.css';
import NavigationBar from './components/NavigationBar';
import AppRoutes from './routes/AppRoutes';

function App() {
  return (
    <div className="App">
      <NavigationBar />
      <AppRoutes/>
    </div>
  );
}

export default App;