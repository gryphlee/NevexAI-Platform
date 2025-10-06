"use client";

// This component now simply receives student data and displays it.
export default function StudentTable({ students }) {

    if (!students || students.length === 0) {
        // This message will likely not show because the parent handles the empty case,
        // but it's good practice to have it.
        return (
            <div className="bg-gray-900/50 border border-cyan-400/30 rounded-lg p-6 text-center">
                <h3 className="text-xl font-bold mb-4 text-cyan-300">All Students</h3>
                <p className="text-gray-500">No student data available.</p>
            </div>
        );
    }

    return (
        <div className="bg-gray-900/50 border border-cyan-400/30 rounded-lg p-6 overflow-x-auto">
            <h3 className="text-xl font-bold mb-4 text-cyan-300">All Students</h3>
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm whitespace-nowrap">
                    <thead className="border-b border-cyan-400/30 text-gray-300">
                        <tr>
                            <th className="p-3">Student ID</th>
                            <th className="p-3">Department</th>
                            <th className="p-3">Year Level</th>
                            <th className="p-3">Quiz Avg</th>
                            <th className="p-3">Attendance %</th>
                            <th className="p-3">Risk Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {students.map((student) => (
                            <tr key={student.student_id} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors">
                                <td className="p-3 font-medium">{student.student_id}</td>
                                <td className="p-3 text-gray-400">{student.department || 'N/A'}</td>
                                <td className="p-3 text-gray-400">{student.year_level || 'N/A'}</td>
                                <td className="p-3">{student.quiz_avg}</td>
                                <td className="p-3">{student.attendance_percentage}%</td>
                                <td className={`p-3 font-bold ${student.at_risk === 1 ? 'text-red-500' : 'text-green-500'}`}>
                                    {student.at_risk_status}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
