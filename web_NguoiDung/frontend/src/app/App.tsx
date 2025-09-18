import { BrowserRouter as Router } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AppProvider } from './AppProvider';
import { AppRoutes } from './AppRoutes';
import { GlobalNotifications } from './GlobalNotifications';
import { DevelopmentBadge } from '../components/common/DevelopmentBadge';
import './styles/App.css';

function App() {
  return (
    <Router>
      <AppProvider>
        <div className="App">
          <DevelopmentBadge />
          <GlobalNotifications />
          <AppRoutes />
          <Toaster 
            position="top-center"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </div>
      </AppProvider>
    </Router>
  );
}

export default App;
