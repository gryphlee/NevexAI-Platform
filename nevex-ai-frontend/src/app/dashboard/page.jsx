"use client";

import { useEffect, useState } from "react";

export default function TeacherDashboardPage() {
  const [students, setStudents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const fetchStudents = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/students");
        if (!response.ok) {
          throw new Error("Failed to fetch student data.");
        }
        const data = await response.json();
        if (isMounted) {
          setStudents(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        if (isMounted) setError(err.message);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    fetchStudents();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Teacher Dashboard</h1>

      <div className="bg-gray-900/50 border border-cyan-400/20 rounded-xl p-6">
        {isLoading && <p className="text-gray-400">Loading students...</p>}
        {error && <p className="text-red-500">Error: {error}</p>}

        {!isLoading && !error && (
          students.length === 0 ? (
            <p className="text-gray-400">No student data available.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm whitespace-nowrap">
                <thead className="text-gray-300 border-b border-cyan-400/20">
                  <tr>
                    <th className="p-3 text-left">Student ID</th>
                    <th className="p-3 text-left">At-Risk Status</th>
                    <th className="p-3 text-left">Quiz Avg</th>
                    <th className="p-3 text-left">Attendance %</th>
                    <th className="p-3 text-left">LMS Hours</th>
                    <th className="p-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((s) => {
                    const isAtRisk = (s.at_risk_status || "").toLowerCase() === "at-risk" || s.at_risk === 1;
                    return (
                      <tr key={s.student_id} className="border-b border-gray-800 hover:bg-gray-800/40 transition-colors">
                        <td className="p-3 font-medium text-white">{s.student_id}</td>
                        <td className="p-3">
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-semibold border ${
                              isAtRisk
                                ? "bg-red-500/10 text-red-400 border-red-500/30"
                                : "bg-green-500/10 text-green-400 border-green-500/30"
                            }`}
                          >
                            {s.at_risk_status || (isAtRisk ? "At-Risk" : "Not At-Risk")}
                          </span>
                        </td>
                        <td className="p-3 text-gray-200">{s.quiz_avg ?? 0}</td>
                        <td className="p-3 text-gray-200">{s.attendance_percentage ?? 0}%</td>
                        <td className="p-3 text-gray-200">{s.lms_hours ?? 0}</td>
                        <td className="p-3">
                          <button
                            type="button"
                            className="inline-flex items-center px-3 py-1.5 rounded-md bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-medium transition-colors"
                            onClick={() => {}}
                          >
                            View Details
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )
        )}
      </div>
    </div>
  );
}
