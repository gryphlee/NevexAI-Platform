"use client";

import { useState } from 'react';
import Papa from 'papaparse';

// These are the columns our system requires
const REQUIRED_COLUMNS = {
    'student_id': 'Unique Student ID',
    'quiz_avg': 'Quiz Average (%)',
    'assignment_submissions': 'Assignments Submitted (Count)',
    'attendance_percentage': 'Attendance (%)',
    'lms_hours': 'LMS Engagement (Hours)',
    'department': 'Student Department',
    'year_level': 'Year Level',
};

export default function CsvUploader() {
    const [file, setFile] = useState(null);
    const [fileHeaders, setFileHeaders] = useState([]);
    const [mapping, setMapping] = useState({});
    const [status, setStatus] = useState({ message: '', type: '' }); // type can be 'success' or 'error'

    const handleFileChange = (e) => {
        const uploadedFile = e.target.files[0];
        if (uploadedFile) {
            setFile(uploadedFile);
            // Parse headers from the CSV
            Papa.parse(uploadedFile, {
                header: true,
                preview: 1, // We only need the first row to get headers
                complete: (results) => {
                    const headers = results.meta.fields;
                    setFileHeaders(headers);
                    // Make a best guess for initial mapping
                    const initialMapping = {};
                    Object.keys(REQUIRED_COLUMNS).forEach(reqCol => {
                        const bestGuess = headers.find(h => h.toLowerCase().includes(reqCol.toLowerCase())) || headers[0];
                        initialMapping[reqCol] = bestGuess;
                    });
                    setMapping(initialMapping);
                }
            });
        }
    };

    const handleMappingChange = (reqCol, selectedCol) => {
        setMapping(prev => ({ ...prev, [reqCol]: selectedCol }));
    };

    const handleImport = async () => {
        if (!file) {
            setStatus({ message: 'Please select a file first.', type: 'error' });
            return;
        }
        setStatus({ message: 'Processing file...', type: 'info' });

        Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            complete: async (results) => {
                try {
                    const jsonData = results.data;
                    // Create the final data to be sent, based on the mapping
                    const dataToImport = jsonData.map(row => {
                        const newRow = {};
                        for (const reqCol in mapping) {
                            newRow[reqCol] = row[mapping[reqCol]];
                        }
                        // Add default values for fields not in mapping, if any
                        newRow['at_risk_status'] = 'Not Evaluated';
                        return newRow;
                    });
                    
                    // Convert back to CSV string to send to the backend
                    const csvToSend = Papa.unparse(dataToImport);
                    const blob = new Blob([csvToSend], { type: 'text/csv' });
                    const formData = new FormData();
                    formData.append('file', blob, 'mapped_data.csv');

                    const token = localStorage.getItem('accessToken');
                    const response = await fetch('http://127.0.0.1:8000/students/upload', {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` },
                        body: formData,
                    });

                    const result = await response.json();
                    if (!response.ok) throw new Error(result.detail || 'Backend error.');
                    
                    setStatus({ message: result.message, type: 'success' });
                    // Optionally, you can trigger a page refresh or data reload here
                    window.location.reload(); // Simple way to refresh data on the page
                } catch (err) {
                    setStatus({ message: `Import failed: ${err.message}`, type: 'error' });
                }
            }
        });
    };

    return (
        <div className="bg-gray-900/50 border border-green-400/30 rounded-lg p-6">
            <h3 className="text-xl font-bold mb-4 text-green-300">Upload & Map New Student Data</h3>
            
            <div className="mb-4">
                <label htmlFor="file-upload" className="block text-sm font-medium text-gray-300 mb-2">Upload any student CSV file</label>
                <input 
                    id="file-upload"
                    type="file" 
                    accept=".csv" 
                    onChange={handleFileChange} 
                    className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-green-600/20 file:text-green-300 hover:file:bg-green-600/40"
                />
            </div>

            {fileHeaders.length > 0 && (
                <>
                    <p className="text-gray-400 mb-4 text-sm">Map your CSV columns to our system's required fields.</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4 mb-6">
                        {Object.entries(REQUIRED_COLUMNS).map(([reqCol, reqDesc]) => (
                            <div key={reqCol}>
                                <label className="block text-sm font-bold text-gray-300" htmlFor={`map-${reqCol}`}>{reqDesc}</label>
                                <p className="text-xs text-gray-500 mb-2">System needs: <span className="font-mono">{reqCol}</span></p>
                                <select
                                    id={`map-${reqCol}`}
                                    name={`map-${reqCol}`}
                                    value={mapping[reqCol] || ''}
                                    onChange={(e) => handleMappingChange(reqCol, e.target.value)}
                                    className="w-full bg-gray-800 rounded p-2 border border-gray-700 focus:outline-none focus:border-green-500"
                                >
                                    <option value="" disabled>Select your column</option>
                                    {fileHeaders.map(header => (
                                        <option key={header} value={header}>{header}</option>
                                    ))}
                                </select>
                            </div>
                        ))}
                    </div>
                    
                    <button onClick={handleImport} className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors">
                        Process and Import Data
                    </button>

                    {status.message && (
                        <p className={`text-sm mt-4 text-center ${
                            status.type === 'success' ? 'text-green-400' :
                            status.type === 'error' ? 'text-red-400' : 'text-gray-400'
                        }`}>
                            {status.message}
                        </p>
                    )}
                </>
            )}
        </div>
    );
}
