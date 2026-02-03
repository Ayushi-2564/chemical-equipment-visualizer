import React, { useState } from 'react';

function UploadCSV({ token, apiUrl, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid CSV file');
      setFile(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${apiUrl}/datasets/upload/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(`Successfully uploaded ${file.name}!`);
        setFile(null);
        document.getElementById('file-input').value = '';
        
        setTimeout(() => {
          onUploadSuccess();
        }, 1500);
      } else {
        setError(data.error || 'Upload failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>📤 Upload CSV File</h2>
      
      <div className="upload-instructions">
        <h3>Required CSV Format:</h3>
        <ul>
          <li>Equipment Name</li>
          <li>Type</li>
          <li>Flowrate</li>
          <li>Pressure</li>
          <li>Temperature</li>
        </ul>
      </div>

      <form onSubmit={handleSubmit} className="upload-form">
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        
        <div className="file-input-wrapper">
          <input
            id="file-input"
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            disabled={uploading}
          />
          {file && <p className="selected-file">Selected: {file.name}</p>}
        </div>

        <button 
          type="submit" 
          disabled={uploading || !file}
          className="btn-primary"
        >
          {uploading ? 'Uploading...' : 'Upload CSV'}
        </button>
      </form>

      <div className="sample-data-section">
        <h3>Sample CSV Data:</h3>
        <pre className="csv-preview">
Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-A1,Reactor,150.5,25.3,350.2
Heat-Exchanger-B2,Heat Exchanger,200.8,15.7,280.5
Pump-C3,Pump,180.2,45.6,85.3
        </pre>
      </div>
    </div>
  );
}

export default UploadCSV;