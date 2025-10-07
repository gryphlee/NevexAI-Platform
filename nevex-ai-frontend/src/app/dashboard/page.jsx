"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

export default function TeacherDashboardPage() {
  const [students, setStudents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState("student_id");
  const [sortDir, setSortDir] = useState("asc");
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const router = useRouter();

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

  const metrics = useMemo(() => {
    const total = students.length;
    const atRisk = students.filter(
      (s) => (s.at_risk_status || "").toLowerCase() === "at-risk" || s.at_risk === 1
    ).length;
    const atRiskPct = total ? Math.round((atRisk / total) * 1000) / 10 : 0;
    return { total, atRisk, atRiskPct };
  }, [students]);

  const filtered = useMemo(() => {
    if (!search) return students;
    const q = search.toLowerCase();
    return students.filter((s) =>
      String(s.student_id).includes(q) ||
      (s.at_risk_status || "").toLowerCase().includes(q) ||
      (s.department || "").toLowerCase().includes(q) ||
      (s.year_level || "").toLowerCase().includes(q)
    );
  }, [students, search]);

  const sorted = useMemo(() => {
    const arr = [...filtered];
    arr.sort((a, b) => {
      const aVal = a[sortKey] ?? 0;
      const bVal = b[sortKey] ?? 0;
      if (aVal < bVal) return sortDir === "asc" ? -1 : 1;
      if (aVal > bVal) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
    return arr;
  }, [filtered, sortKey, sortDir]);

  const totalPages = Math.max(1, Math.ceil(sorted.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const paged = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sorted.slice(start, start + pageSize);
  }, [sorted, currentPage]);

  const toggleSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Teacher Dashboard</h1>

      {/* Top metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-gray-900/50 border border-cyan-400/20 rounded-xl p-4">
          <p className="text-sm text-gray-400">Total Students</p>
          <p className="text-3xl font-bold text-white">{metrics.total}</p>
        </div>
        <div className="bg-gray-900/50 border border-red-400/20 rounded-xl p-4">
          <p className="text-sm text-gray-400">At-Risk</p>
          <p className="text-3xl font-bold text-red-400">{metrics.atRisk}</p>
        </div>
        <div className="bg-gray-900/50 border border-amber-400/20 rounded-xl p-4">
          <p className="text-sm text-gray-400">At-Risk %</p>
          <p className="text-3xl font-bold text-amber-300">{metrics.atRiskPct}%</p>
        </div>
      </div>

      <div className="bg-gray-900/50 border border-cyan-400/20 rounded-xl p-6">
        {isLoading && <p className="text-gray-400">Loading students...</p>}
        {error && <p className="text-red-500">Error: {error}</p>}

        {!isLoading && !error && (
          students.length === 0 ? (
            <p className="text-gray-400">No student data available.</p>
          ) : (
            <>
              <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between mb-4">
                <input
                  type="text"
                  value={search}
                  onChange={(e) => { setPage(1); setSearch(e.target.value); }}
                  placeholder="Search by ID, status, department, year..."
                  className="w-full sm:max-w-xs bg-gray-800 rounded-md px-3 py-2 border border-gray-700 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                />
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <span>Sort:</span>
                  <select
                    className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-gray-200"
                    value={sortKey}
                    onChange={(e) => setSortKey(e.target.value)}
                  >
                    <option value="student_id">Student ID</option>
                    <option value="quiz_avg">Quiz Avg</option>
                    <option value="attendance_percentage">Attendance %</option>
                    <option value="lms_hours">LMS Hours</option>
                  </select>
                  <button
                    className="px-2 py-1 rounded bg-gray-800 border border-gray-700 hover:border-cyan-500"
                    onClick={() => setSortDir((d) => (d === "asc" ? "desc" : "asc"))}
                  >
                    {sortDir === "asc" ? "Asc" : "Desc"}
                  </button>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full text-sm whitespace-nowrap">
                  <thead className="text-gray-300 border-b border-cyan-400/20">
                    <tr>
                      <th className="p-3 text-left cursor-pointer" onClick={() => toggleSort('student_id')}>Student ID</th>
                      <th className="p-3 text-left">At-Risk Status</th>
                      <th className="p-3 text-left cursor-pointer" onClick={() => toggleSort('quiz_avg')}>Quiz Avg</th>
                      <th className="p-3 text-left cursor-pointer" onClick={() => toggleSort('attendance_percentage')}>Attendance %</th>
                      <th className="p-3 text-left cursor-pointer" onClick={() => toggleSort('lms_hours')}>LMS Hours</th>
                      <th className="p-3 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paged.map((s) => {
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
                              onClick={() => router.push(`/dashboard/students/${s.student_id}`)}
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

              <div className="flex items-center justify-between mt-4 text-sm text-gray-400">
                <span>
                  Page {currentPage} of {totalPages}
                </span>
                <div className="flex items-center gap-2">
                  <button
                    className="px-3 py-1 rounded bg-gray-800 border border-gray-700 disabled:opacity-50"
                    disabled={currentPage <= 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                  >
                    Prev
                  </button>
                  <button
                    className="px-3 py-1 rounded bg-gray-800 border border-gray-700 disabled:opacity-50"
                    disabled={currentPage >= totalPages}
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          )
        )}
      </div>
    </div>
  );
}
