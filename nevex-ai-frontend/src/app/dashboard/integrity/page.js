"use client";

import { useEffect, useState, useMemo } from "react";

export default function IntegrityDashboardPage() {
  const [students, setStudents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
    const fetchStudents = async () => {
      setIsLoading(true);
      try {
        const response = await fetch("http://127.0.0.1:8000/students", {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
        if (!response.ok) throw new Error("Failed to fetch student data.");
        const data = await response.json();
        setStudents(Array.isArray(data) ? data : []);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStudents();
  }, []);

  const integrityStats = useMemo(() => {
    const total = students.length;
    const atRisk = students.filter((s) => (s.at_risk_status || '').toLowerCase() === 'at-risk').length;
    return { total, atRisk, notAtRisk: total - atRisk };
  }, [students]);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Integrity Dashboard</h2>
        <p className="text-gray-400">Monitor potential academic integrity risks and anomalies across students.</p>
      </div>

      <div className="bg-gray-900/50 border border-amber-400/30 rounded-lg p-6">
        {isLoading && <p className="text-gray-400">Loading...</p>}
        {error && <p className="text-red-500">Error: {error}</p>}
        {!isLoading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-sm text-gray-400">Total Students</p>
              <p className="text-3xl font-bold text-white">{integrityStats.total}</p>
            </div>
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-sm text-gray-400">At-Risk</p>
              <p className="text-3xl font-bold text-red-400">{integrityStats.atRisk}</p>
            </div>
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-sm text-gray-400">Not At-Risk</p>
              <p className="text-3xl font-bold text-green-400">{integrityStats.notAtRisk}</p>
            </div>
          </div>
        )}
      </div>

      <div className="bg-gray-900/50 border border-cyan-400/30 rounded-lg p-6">
        <h3 className="text-xl font-bold mb-4 text-cyan-300">Recent Flags</h3>
        <p className="text-gray-500">No integrity events API yet; this section will show recent anomalies once available.</p>
      </div>
    </div>
  );
}
