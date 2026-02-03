import React, { useState, useEffect } from 'react';
import { Bar, Line } from 'react-chartjs-2';

function DatasetDetail({ token, apiUrl, datasetId, onBack }) {
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDataset();
  }, [datasetId]);

  const fetchDataset = async () => {
    try {
      const response = await fetch(`${apiUrl}/datasets/${datasetId}/`, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDataset(data);
      } else {
        setError('Failed to fetch dataset details');
      }
    } catch (error) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async () => {
    try {
      const response = await fetch(`${apiUrl}/datasets/${datasetId}/report/`, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${dataset.filename}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    } catch (error) {
      console.error('Error downloading PDF:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading dataset...</div>;
  }

  if (error || !dataset) {
    return <div className="error-message">{error}</div>;
  }

  const typeChartData = {
    labels: Object.keys(dataset.type_distribution),
    datasets: [{
      label: 'Equipment Count',
      data: Object.values(dataset.type_distribution),
      backgroundColor: '#3498db'
    }]
  };

  return (
    <div className="dataset-detail">
      <div className="detail-header">
        <button onClick={onBack} className="btn-back">← Back</button>
        <h2>{dataset.filename}</h2>
        <button onClick={downloadPDF} className="btn-primary">📄 Download PDF</button>
      </div>

      <div className="detail-stats">
        <div className="stat-item">
          <strong>Total Equipment:</strong> {dataset.total_count}
        </div>
        <div className="stat-item">
          <strong>Avg Flowrate:</strong> {dataset.avg_flowrate.toFixed(2)} m³/h
        </div>
        <div className="stat-item">
          <strong>Avg Pressure:</strong> {dataset.avg_pressure.toFixed(2)} bar
        </div>
        <div className="stat-item">
          <strong>Avg Temperature:</strong> {dataset.avg_temperature.toFixed(2)} °C
        </div>
      </div>

      <div className="chart-section">
        <h3>Equipment Type Distribution</h3>
        <Bar data={typeChartData} />
      </div>

      <div className="equipment-table-section">
        <h3>Equipment Details</h3>
        <div className="table-wrapper">
          <table className="equipment-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Flowrate</th>
                <th>Pressure</th>
                <th>Temperature</th>
              </tr>
            </thead>
            <tbody>
              {dataset.equipment.map(eq => (
                <tr key={eq.id}>
                  <td>{eq.equipment_name}</td>
                  <td>{eq.equipment_type}</td>
                  <td>{eq.flowrate.toFixed(1)}</td>
                  <td>{eq.pressure.toFixed(1)}</td>
                  <td>{eq.temperature.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default DatasetDetail;