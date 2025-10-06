"use client";

import { useEffect, useState } from 'react';
import AnalyticsDashboard from '../AnalyticsDashboard'; // We reuse the component from before

export default function AnalyticsPage() {
    const [students, setStudents] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        if (!token) return;

        const fetchStudents = async () => {
            setIsLoading(true);
            try {
                const response = await fetch('http://127.0.0.1:8000/students', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) { throw new Error(`Failed to fetch student data.`); }
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

    return (
        <div>
            <h2 className="text-3xl font-bold text-white mb-8">Analytics Hub</h2>
            
            {isLoading && <p className="text-gray-400">Loading analytics data...</p>}
            {error && <p className="text-red-500">Error: {error}</p>}

            {!isLoading && !error && (
                <AnalyticsDashboard students={students} />
            )}
        </div>
    );
}