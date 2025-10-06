"use client";

import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useMemo } from 'react';

const COLORS = ['#A855F7', '#10B981']; // Purple for At-Risk, Green for Not At-Risk

// Custom Label for Pie Chart to handle 0% case better
const RADIAN = Math.PI / 180;
const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, name }) => {
  if (percent === 0) return null; // Don't show label for 0% slice
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text x={x} y={y} fill="white" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central" fontSize={14}>
      {`${name} (${(percent * 100).toFixed(0)}%)`}
    </text>
  );
};

export default function AnalyticsDashboard({ students }) {
    const riskDistributionData = useMemo(() => {
        if (!students || students.length === 0) return [];
        const atRiskCount = students.filter(s => s.at_risk === 1).length;
        const notAtRiskCount = students.length - atRiskCount;
        return [
            { name: 'At-Risk', value: atRiskCount },
            { name: 'Not At-Risk', value: notAtRiskCount },
        ];
    }, [students]);

    // ... (quizAvgByDeptData remains the same)
    const quizAvgByDeptData = useMemo(() => {
        if (!students || students.length === 0) return [];
        const deptData = {};
        students.forEach(student => {
            const dept = student.department || 'Unknown';
            if (!deptData[dept]) {
                deptData[dept] = { totalScore: 0, count: 0 };
            }
            deptData[dept].totalScore += student.quiz_avg;
            deptData[dept].count++;
        });
        return Object.keys(deptData).map(dept => ({
            name: dept,
            'Average Quiz Score': parseFloat((deptData[dept].totalScore / deptData[dept].count).toFixed(2)),
        }));
    }, [students]);

    if (!students || students.length === 0) {
        return null;
    }

    return (
        <div className="bg-gray-900/50 border border-amber-400/30 rounded-lg p-6 mb-8">
            <h3 className="text-xl font-bold mb-6 text-amber-300">Analytics Hub</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8" style={{ minHeight: '350px' }}>
                <div>
                    <h4 className="text-lg font-semibold text-center mb-4">Student Risk Distribution</h4>
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={riskDistributionData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                outerRadius={120}
                                fill="#8884d8"
                                dataKey="value"
                                label={renderCustomizedLabel} // Use our custom label
                            >
                                {riskDistributionData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                <div>
                    <h4 className="text-lg font-semibold text-center mb-4">Average Quiz Scores by Department</h4>
                     <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={quizAvgByDeptData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                            <XAxis dataKey="name" stroke="#94A3B8" fontSize={12} tick={{ fill: '#94A3B8' }} />
                            <YAxis stroke="#94A3B8" tick={{ fill: '#94A3B8' }} />
                            <Tooltip cursor={{fill: 'rgba(136, 132, 216, 0.1)'}} contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
                            <Legend wrapperStyle={{ color: '#94A3B8' }}/>
                            <Bar dataKey="Average Quiz Score" fill={'#00F0FF'} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}
