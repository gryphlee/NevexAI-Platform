"use client";

import StudentTable from './StudentTable';
import UserManagement from './UserManagement';
import { useEffect, useState } from 'react';

export default function OverviewPage() {
    const [students, setStudents] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [userRole, setUserRole] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            const [, role] = token.split(':');
            setUserRole(role);
        }

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
            <h2 className="text-3xl font-bold text-white mb-8">Dashboard Overview</h2>
            
            {isLoading && <p className="text-gray-400">Loading modules...</p>}
            {error && <p className="text-red-500">Error: {error}</p>}

            {!isLoading && !error && (
                <div className="space-y-8">
                    {userRole === 'Admin' && <UserManagement />}
                    <StudentTable students={students} />
                </div>
            )}
        </div>
    );
}
