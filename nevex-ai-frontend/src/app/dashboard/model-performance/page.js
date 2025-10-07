"use client";

import { useEffect, useState } from "react";

export default function ModelPerformancePage() {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      setIsLoading(true);
      try {
        const response = await fetch("http://127.0.0.1:8000/api/dashboard-stats");
        if (!response.ok) throw new Error("Failed to fetch model performance stats.");
        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Model Performance</h2>
        <p className="text-gray-400">High-level KPIs and diagnostics for AI components.</p>
      </div>

      <div className="bg-gray-900/50 border border-cyan-400/30 rounded-lg p-6">
        {isLoading && <p className="text-gray-400">Loading...</p>}
        {error && <p className="text-red-500">Error: {error}</p>}
        {!isLoading && !error && stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-sm text-gray-400">Success Rate</p>
              <p className="text-3xl font-bold text-white">{stats.successRate}%</p>
            </div>
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-sm text-gray-400">Intervention Speed</p>
              <p className="text-3xl font-bold text-white">{stats.interventionSpeed} days</p>
            </div>
            <div className="bg-gray-800/50 p-4 rounded-lg">
              <p className="text-sm text-gray-400">Agent Success Rate</p>
              <p className="text-3xl font-bold text-white">{stats.agentSuccessRate}%</p>
            </div>
          </div>
        )}
      </div>

      <div className="bg-gray-900/50 border border-purple-400/30 rounded-lg p-6">
        <h3 className="text-xl font-bold mb-4 text-purple-300">Additional Metrics</h3>
        {!isLoading && !error && stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-300">
            <div>
              <p className="text-sm text-gray-400">Active Agents</p>
              <p className="text-2xl font-bold text-white">{stats.agentPerformance?.activeAgents}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Detection vs Manual</p>
              <p className="text-2xl font-bold text-white">{stats.detectionVsManual}</p>
            </div>
          </div>
        )}
        {(!stats && !isLoading && !error) && (
          <p className="text-gray-500">No stats available.</p>
        )}
      </div>
    </div>
  );
}
