"use client";

import { useEffect, useState, useMemo } from 'react';
import CsvUploader from './CsvUploader'; // <-- IMPORT THE NEW COMPONENT

// ... (MetricCard component remains the same)
const MetricCard = ({ title, value, helpText }) => (
    <div className="bg-gray-800/50 p-6 rounded-lg">
        <h4 className="text-gray-400 text-sm font-medium">{title}</h4>
        <p className="text-3xl font-bold text-white mt-1">{value}</p>
        {helpText && <p className="text-xs text-gray-500 mt-2">{helpText}</p>}
    </div>
);


export default function DatabaseAdminPage() {
    const [students, setStudents] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [linkStatus, setLinkStatus] = useState({ message: '', error: false });

    useEffect(() => {
        // ... (useEffect logic remains the same)
        const token = localStorage.getItem('accessToken');
        if (!token) {
            setError("Authentication required.");
            setIsLoading(false);
            return;
        }

        const fetchStudents = async () => {
            setIsLoading(true);
            try {
                const response = await fetch('http://127.0.0.1:8000/students', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error(`Failed to fetch student data.`);
                const data = await response.json();
                setStudents(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };
        
        fetchStudents();
    }, []);

    const healthMetrics = useMemo(() => {
        // ... (healthMetrics logic remains the same)
        if (!students || students.length === 0) {
            return { totalRecords: 0, missingData: 0, uniqueDepts: 0 };
        }
        const df = students; 
        const missingData = df.reduce((acc, student) => {
            return acc + Object.values(student).filter(val => val === null || val === undefined).length;
        }, 0);
        const uniqueDepts = new Set(df.map(s => s.department)).size;

        return {
            totalRecords: df.length,
            missingData: missingData,
            uniqueDepts: uniqueDepts,
        };
    }, [students]);

    const handleLinkParent = async (event) => {
        // ... (handleLinkParent logic remains the same)
         event.preventDefault();
        setLinkStatus({ message: '', error: false });

        const formData = new FormData(event.target);
        const student_id = parseInt(formData.get('student_id'), 10);
        const parent_username = formData.get('parent_username');

        if (!student_id || !parent_username) {
            setLinkStatus({ message: 'Both fields are required.', error: true });
            return;
        }

        try {
            const token = localStorage.getItem('accessToken');
            const response = await fetch('http://127.0.0.1:8000/students/link-parent', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ student_id, parent_username }),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || "Failed to link accounts.");
            
            setLinkStatus({ message: result.message, error: false });
            event.target.reset();
        } catch (err) {
            setLinkStatus({ message: err.message, error: true });
        }
    };

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-3xl font-bold text-white mb-2">Data Engineering Control Panel</h2>
                <p className="text-gray-400">Monitor data health, validate new uploads, and manage database records.</p>
            </div>
            
            <div className="bg-gray-900/50 border border-cyan-400/30 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4 text-cyan-300">Database Health Check</h3>
                {isLoading ? (
                    <p>Loading health metrics...</p>
                ) : error ? (
                    <p className="text-red-500">{error}</p>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <MetricCard title="Total Student Records" value={healthMetrics.totalRecords.toLocaleString()} />
                        <MetricCard title="Missing Data Points" value={healthMetrics.missingData.toLocaleString()} helpText="Total number of empty cells."/>
                        <MetricCard title="Unique Departments" value={healthMetrics.uniqueDepts} />
                    </div>
                )}
            </div>

            {/* REPLACE THE "Coming Soon" WITH THE NEW COMPONENT */}
            <CsvUploader />

            <div className="bg-gray-900/50 border border-purple-400/30 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4 text-purple-300">🔗 Link Parent to Student Account</h3>
                <form onSubmit={handleLinkParent} className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
                    <div>
                        <label className="block text-gray-400 text-sm mb-2" htmlFor="student_id">Student ID</label>
                        <input className="w-full bg-gray-800 rounded p-2 border border-gray-700 focus:outline-none focus:border-purple-500" type="number" name="student_id" id="student_id" placeholder="e.g., 2025001" />
                    </div>
                    <div>
                        <label className="block text-gray-400 text-sm mb-2" htmlFor="parent_username">Parent Username</label>
                        <input className="w-full bg-gray-800 rounded p-2 border border-gray-700 focus:outline-none focus:border-purple-500" type="text" name="parent_username" id="parent_username" placeholder="e.g., parent_juan" />
                    </div>
                    <button type="submit" className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded transition-colors">
                        Link Accounts
                    </button>
                </form>
                {linkStatus.message && (
                    <p className={`text-sm mt-4 text-center ${linkStatus.error ? 'text-red-500' : 'text-green-500'}`}>{linkStatus.message}</p>
                )}
            </div>
        </div>
    );
}
