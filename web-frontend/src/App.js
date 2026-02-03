
import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import UploadCSV from './components/UploadCSV';
import DatasetList from './components/DatasetList';
import DatasetDetail from './components/DatasetDetail';

const API_URL = 'http://localhost:8000/api';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedDataset, setSelectedDataset] = useState(null);

  useEffect(() => {
    if (token) {
      fetchUser();
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await fetch(`${API_URL}/auth/user/`, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        handleLogout();
      }
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  };

  const handleLogin = (token, userData) => {
    setToken(token);
    setUser(userData);
    localStorage.setItem('token', token);
  };

  const handleLogout = async () => {
    try {
      await fetch(`${API_URL}/auth/logout/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`
        }
      });
    } catch (error) {
      console.error('Error logging out:', error);
    }
    
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    setCurrentView('dashboard');
  };

  const handleDatasetSelect = (dataset) => {
    setSelectedDataset(dataset);
    setCurrentView('detail');
  };

  if (!token) {
    return (
      <div className="App">
        <div className="auth-container">
          <div className="auth-header">
            <h1>🧪 Chemical Equipment Visualizer</h1>
            <p>Analyze and visualize chemical equipment data</p>
          </div>
          <AuthTabs onLogin={handleLogin} />
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>🧪 Chemical Equipment Visualizer</h1>
          <div className="user-info">
            <span>Welcome, {user?.username}!</span>
            <button onClick={handleLogout} className="btn-logout">Logout</button>
          </div>
        </div>
      </header>

      <nav className="app-nav">
        <button 
          className={currentView === 'dashboard' ? 'active' : ''}
          onClick={() => setCurrentView('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={currentView === 'upload' ? 'active' : ''}
          onClick={() => setCurrentView('upload')}
        >
          📤 Upload CSV
        </button>
        <button 
          className={currentView === 'history' ? 'active' : ''}
          onClick={() => setCurrentView('history')}
        >
          📜 History
        </button>
      </nav>

      <main className="app-main">
        {currentView === 'dashboard' && <Dashboard token={token} apiUrl={API_URL} />}
        {currentView === 'upload' && (
          <UploadCSV 
            token={token} 
            apiUrl={API_URL} 
            onUploadSuccess={() => setCurrentView('history')}
          />
        )}
        {currentView === 'history' && (
          <DatasetList 
            token={token} 
            apiUrl={API_URL}
            onDatasetSelect={handleDatasetSelect}
          />
        )}
        {currentView === 'detail' && selectedDataset && (
          <DatasetDetail 
            token={token} 
            apiUrl={API_URL}
            datasetId={selectedDataset.id}
            onBack={() => setCurrentView('history')}
          />
        )}
      </main>
    </div>
  );
}

function AuthTabs({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="auth-tabs">
      <div className="tab-buttons">
        <button 
          className={isLogin ? 'active' : ''}
          onClick={() => setIsLogin(true)}
        >
          Login
        </button>
        <button 
          className={!isLogin ? 'active' : ''}
          onClick={() => setIsLogin(false)}
        >
          Register
        </button>
      </div>
      
      {isLogin ? (
        <Login onLogin={onLogin} />
      ) : (
        <Register onRegister={onLogin} />
      )}
    </div>
  );
}

export default App;