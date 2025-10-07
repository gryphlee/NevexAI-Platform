"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

export default function StudentDetailsPage() {
  const params = useParams();
  const studentIdParam = params?.id;
  const studentId = useMemo(() => {
    const parsed = parseInt(Array.isArray(studentIdParam) ? studentIdParam[0] : studentIdParam, 10);
    return Number.isNaN(parsed) ? null : parsed;
  }, [studentIdParam]);

  const [students, setStudents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStudents = async () => {
      setIsLoading(true);
      try {
        const response = await fetch("http://127.0.0.1:8000/students");
        if (!response.ok) throw new Error("Failed to fetch students");
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

  const student = useMemo(() => {
    if (!studentId) return null;
    return students.find((s) => Number(s.student_id) === studentId) || null;
  }, [students, studentId]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Student Details</h1>
        <Link href="/dashboard" className="text-sm px-3 py-2 rounded-md bg-cyan-600 hover:bg-cyan-700 text-white transition-colors">
          Back to Dashboard
        </Link>
      </div>

      <div className="bg-gray-900/50 border border-cyan-400/20 rounded-xl p-6">
        {isLoading && <p className="text-gray-400">Loading...</p>}
        {error && <p className="text-red-500">Error: {error}</p>}

        {!isLoading && !error && (
          !student ? (
            <p className="text-gray-400">Student not found.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <h2 className="text-xl font-semibold text-white">Profile</h2>
                <div className="text-gray-300">
                  <p><span className="text-gray-400">Student ID:</span> <span className="text-white font-medium">{student.student_id}</span></p>
                  <p><span className="text-gray-400">At-Risk Status:</span> <span className={`font-semibold ${((student.at_risk_status||'').toLowerCase()==='at-risk'||student.at_risk===1)?'text-red-400':'text-green-400'}`}>{student.at_risk_status || (student.at_risk===1? 'At-Risk':'Not At-Risk')}</span></p>
                  <p><span className="text-gray-400">Department:</span> {student.department || 'N/A'}</p>
                  <p><span className="text-gray-400">Year Level:</span> {student.year_level || 'N/A'}</p>
                  <p><span className="text-gray-400">Parent Username:</span> {student.parent_username || 'N/A'}</p>
                </div>
              </div>

              <div className="space-y-2">
                <h2 className="text-xl font-semibold text-white">Performance</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-800/50 p-4 rounded-lg">
                    <p className="text-sm text-gray-400">Quiz Avg</p>
                    <p className="text-2xl font-bold text-white">{student.quiz_avg ?? 0}</p>
                  </div>
                  <div className="bg-gray-800/50 p-4 rounded-lg">
                    <p className="text-sm text-gray-400">Attendance %</p>
                    <p className="text-2xl font-bold text-white">{student.attendance_percentage ?? 0}%</p>
                  </div>
                  <div className="bg-gray-800/50 p-4 rounded-lg">
                    <p className="text-sm text-gray-400">LMS Hours</p>
                    <p className="text-2xl font-bold text-white">{student.lms_hours ?? 0}</p>
                  </div>
                  <div className="bg-gray-800/50 p-4 rounded-lg">
                    <p className="text-sm text-gray-400">Assignments</p>
                    <p className="text-2xl font-bold text-white">{student.assignment_submissions ?? 0}</p>
                  </div>
                </div>
              </div>

              <div className="md:col-span-2 bg-gray-800/40 p-4 rounded-lg border border-gray-700">
                <h3 className="text-lg font-semibold text-white mb-2">Notes</h3>
                <p className="text-gray-400">Further details and interventions will appear here.</p>
              </div>
            </div>
          )
        )}
      </div>
    </div>
  );
}
