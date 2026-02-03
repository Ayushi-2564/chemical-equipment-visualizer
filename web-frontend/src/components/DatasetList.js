import React, { useState, useEffect } from 'react';

function DatasetList({ token, apiUrl, onDatasetSelect }) {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const response = await fetch(`${apiUrl}/datasets/`, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDatasets(data);
      } else {
        setError('Failed to fetch datasets');
      }
    } catch (error) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this dataset?')) {
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/datasets/${id}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      if (response.ok) {
        setDatasets(datasets.filter(ds => ds.id !== id));
      }
    } catch (error) {
      console.error('Error deleting dataset:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading datasets...</div>;
  }

  if (datasets.length === 0) {
    return (
      <div className="empty-state">
        <h2>📜 Dataset History</h2>
        <p>No datasets found. Upload a CSV file to get started!</p>
      </div>
    );
  }

  return (
    <div className="dataset-list">
      <h2>📜 Dataset History (Last 5)</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <div className="datasets-grid">
        {datasets.map(dataset => (
          <div key={dataset.id} className="dataset-card">
            <h3>{dataset.filename}</h3>
            <div className="dataset-details">
              <p><strong>Total Equipment:</strong> {dataset.total_count}</p>
              <p><strong>Uploaded:</strong> {new Date(dataset.upload_date).toLocaleString()}</p>
              
              <div className="stats-mini">
                <span>Flowrate: {dataset.avg_flowrate.toFixed(1)}</span>
                <span>Pressure: {dataset.avg_pressure.toFixed(1)}</span>
                <span>Temp: {dataset.avg_temperature.toFixed(1)}</span>
              </div>
            </div>
            
            <div className="dataset-actions">
              <button 
                onClick={() => onDatasetSelect(dataset)}
                className="btn-secondary"
              >
                View Details
              </button>
              <button 
                onClick={() => handleDelete(dataset.id)}
                className="btn-danger"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DatasetList;