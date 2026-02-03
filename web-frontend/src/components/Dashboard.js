import React, { useState, useEffect } from 'react';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

function Dashboard({ token, apiUrl }) {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [latestDataset, setLatestDataset] = useState(null);

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
        if (data.length > 0) {
          setLatestDataset(data[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (!latestDataset) {
    return (
      <div className="empty-state">
        <h2>📊 Welcome to Your Dashboard</h2>
        <p>No datasets uploaded yet. Upload a CSV file to get started!</p>
      </div>
    );
  }

  const typeDistData = {
    labels: Object.keys(latestDataset.type_distribution),
    datasets: [{
      data: Object.values(latestDataset.type_distribution),
      backgroundColor: [
        '#FF6384',
        '#36A2EB',
        '#FFCE56',
        '#4BC0C0',
        '#9966FF',
        '#FF9F40'
      ]
    }]
  };

  const avgParamsData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [{
      label: 'Average Values',
      data: [
        latestDataset.avg_flowrate,
        latestDataset.avg_pressure,
        latestDataset.avg_temperature
      ],
      backgroundColor: ['#3498db', '#e74c3c', '#2ecc71']
    }]
  };

  return (
    <div className="dashboard">
      <h2>Dashboard - Latest Dataset</h2>
      
      <div className="stats-cards">
        <div className="stat-card">
          <h3>Total Equipment</h3>
          <p className="stat-value">{latestDataset.total_count}</p>
        </div>
        <div className="stat-card">
          <h3>Avg Flowrate</h3>
          <p className="stat-value">{latestDataset.avg_flowrate.toFixed(2)}</p>
          <span className="stat-unit">m³/h</span>
        </div>
        <div className="stat-card">
          <h3>Avg Pressure</h3>
          <p className="stat-value">{latestDataset.avg_pressure.toFixed(2)}</p>
          <span className="stat-unit">bar</span>
        </div>
        <div className="stat-card">
          <h3>Avg Temperature</h3>
          <p className="stat-value">{latestDataset.avg_temperature.toFixed(2)}</p>
          <span className="stat-unit">°C</span>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Equipment Type Distribution</h3>
          <Pie data={typeDistData} options={{ maintainAspectRatio: true }} />
        </div>
        
        <div className="chart-container">
          <h3>Average Parameters</h3>
          <Bar data={avgParamsData} options={{
            maintainAspectRatio: true,
            scales: {
              y: { beginAtZero: true }
            }
          }} />
        </div>
      </div>

      <div className="dataset-info">
        <p><strong>Dataset:</strong> {latestDataset.filename}</p>
        <p><strong>Uploaded:</strong> {new Date(latestDataset.upload_date).toLocaleString()}</p>
      </div>
    </div>
  );
}

export default Dashboard;