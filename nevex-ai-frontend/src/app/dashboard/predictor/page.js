"use client";

import { useState, useEffect, useId } from 'react';

// A reusable slider component
const LabeledSlider = ({ label, min, max, value, onChange, disabled = false }) => {
    const id = useId();
    return (
        <div>
            <label htmlFor={id} className={`block text-sm mb-2 ${disabled ? 'text-gray-600' : 'text-gray-400'}`}>{label}: <span className="font-bold text-white">{value}</span></label>
            <input
                id={id}
                name={id}
                type="range"
                min={min}
                max={max}
                value={value}
                onChange={onChange}
                disabled={disabled}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer disabled:bg-gray-800"
            />
        </div>
    );
};

// A reusable metric display component
const ResultMetric = ({ label, value, delta, isAtRisk }) => (
    <div className="bg-gray-800/50 p-4 rounded-lg text-center">
        <h4 className="text-sm font-medium text-gray-400">{label}</h4>
        <p className={`text-2xl font-bold ${isAtRisk ? 'text-red-500' : 'text-green-500'}`}>{value}</p>
        {delta && <p className={`text-sm font-bold ${delta > 0 ? 'text-green-400' : 'text-red-400'}`}>{delta > 0 ? '+' : ''}{delta.toFixed(1)}% vs Original</p>}
    </div>
);


export default function RiskPredictorPage() {
    const [inputData, setInputData] = useState({
        quiz_avg: 78,
        assignment_submissions: 9,
        attendance_percentage: 85,
        lms_hours: 20,
    });
    const [prediction, setPrediction] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    // State for the "What-If" simulator
    const [hypotheticalData, setHypotheticalData] = useState(inputData);
    const [hypotheticalPrediction, setHypotheticalPrediction] = useState(null);
    const [isSimulating, setIsSimulating] = useState(false);

    // This effect runs the simulation whenever the hypothetical sliders are moved
    useEffect(() => {
        if (!prediction) return; // Don't run simulation if there's no base prediction

        const runSimulation = async () => {
            setIsSimulating(true);
            try {
                const token = localStorage.getItem('accessToken');
                const response = await fetch('http://127.0.0.1:8000/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify(hypotheticalData),
                });
                const result = await response.json();
                if (!response.ok) throw new Error(result.detail || "Simulation failed.");
                setHypotheticalPrediction(result);
            } catch (err) {
                // We can show a small error state for the simulation if needed
                console.error("Simulation error:", err);
            } finally {
                setIsSimulating(false);
            }
        };

        const handler = setTimeout(() => {
            runSimulation();
        }, 500); // Debounce: wait 500ms after user stops moving slider

        return () => clearTimeout(handler); // Cleanup on component unmount
    }, [hypotheticalData, prediction]);

    const handleSliderChange = (e, field) => {
        const value = parseInt(e.target.value, 10);
        setInputData(prev => ({ ...prev, [field]: value }));
        // Also update the hypothetical data when original data changes
        setHypotheticalData(prev => ({ ...prev, [field]: value }));
    };

    const handleHypoSliderChange = (e, field) => {
        setHypotheticalData(prev => ({ ...prev, [field]: parseInt(e.target.value, 10) }));
    };

    const handleAnalyze = async () => {
        setIsLoading(true);
        setError('');
        setPrediction(null);
        setHypotheticalPrediction(null);
        setHypotheticalData(inputData); // Reset hypothetical data to match input
        try {
            const token = localStorage.getItem('accessToken');
            const response = await fetch('http://127.0.0.1:8000/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(inputData),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || "Prediction failed.");
            setPrediction(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <h2 className="text-3xl font-bold text-white mb-2">Single Student Risk Predictor</h2>
            <p className="text-gray-400 mb-8">Analyze a student's risk and simulate the impact of interventions in real-time.</p>
            
            <div className="space-y-8">
                {/* Main Analysis Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="bg-gray-900/50 border border-purple-400/30 rounded-lg p-6">
                        <h3 className="text-xl font-bold mb-6 text-purple-300">1. Student Data Input</h3>
                        <div className="space-y-6">
                            <LabeledSlider label="Quiz Average (%)" min={0} max={100} value={inputData.quiz_avg} onChange={(e) => handleSliderChange(e, 'quiz_avg')} />
                            <LabeledSlider label="Assignments Submitted" min={0} max={10} value={inputData.assignment_submissions} onChange={(e) => handleSliderChange(e, 'assignment_submissions')} />
                            <LabeledSlider label="Attendance (%)" min={0} max={100} value={inputData.attendance_percentage} onChange={(e) => handleSliderChange(e, 'attendance_percentage')} />
                            <LabeledSlider label="LMS Hours" min={0} max={50} value={inputData.lms_hours} onChange={(e) => handleSliderChange(e, 'lms_hours')} />
                            <button onClick={handleAnalyze} disabled={isLoading} className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-4 rounded transition-colors disabled:bg-gray-500">
                                {isLoading ? 'Analyzing...' : 'Analyze Student Risk'}
                            </button>
                        </div>
                    </div>
                    <div className="bg-gray-900/50 border border-cyan-400/30 rounded-lg p-6 flex items-center justify-center">
                        {isLoading && <p>Loading prediction...</p>}
                        {error && <p className="text-red-500">{error}</p>}
                        {!prediction && !isLoading && <div className="text-center text-gray-500"><p className="text-4xl mb-4">🤖</p><p>Prediction results will appear here.</p></div>}
                        {prediction && (
                            <div className="text-center">
                                <h3 className="text-lg font-medium text-gray-400 mb-2">Original Prediction</h3>
                                <p className={`text-5xl font-bold ${prediction.risk_status === 'AT-RISK' ? 'text-red-500' : 'text-green-500'}`}>{prediction.risk_status}</p>
                                <div className="mt-6">
                                    <p className="text-gray-400">Probability of Success</p>
                                    <p className="text-3xl font-bold text-cyan-400">{prediction.success_probability}%</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* "What-If" Simulator Section */}
                {prediction && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div className="bg-gray-900/50 border border-amber-400/30 rounded-lg p-6">
                            <h3 className="text-xl font-bold mb-6 text-amber-300">2. Intervention Planner (What-If)</h3>
                            <div className="space-y-6">
                                <LabeledSlider label="Hypothetical Quiz Avg (%)" min={0} max={100} value={hypotheticalData.quiz_avg} onChange={(e) => handleHypoSliderChange(e, 'quiz_avg')} />
                                <LabeledSlider label="Hypothetical Assignments" min={0} max={10} value={hypotheticalData.assignment_submissions} onChange={(e) => handleHypoSliderChange(e, 'assignment_submissions')} />
                                <LabeledSlider label="Hypothetical Attendance (%)" min={0} max={100} value={hypotheticalData.attendance_percentage} onChange={(e) => handleHypoSliderChange(e, 'attendance_percentage')} />
                                <LabeledSlider label="Hypothetical LMS Hours" min={0} max={50} value={hypotheticalData.lms_hours} onChange={(e) => handleHypoSliderChange(e, 'lms_hours')} />
                            </div>
                        </div>
                        <div className="bg-gray-900/50 border border-amber-400/30 rounded-lg p-6">
                            <h3 className="text-xl font-bold mb-6 text-amber-300">3. Simulated Outcome</h3>
                            {isSimulating && <p className="text-center">Simulating...</p>}
                            {hypotheticalPrediction && (
                                <div className="grid grid-cols-2 gap-4">
                                    <ResultMetric 
                                        label="Original Status" 
                                        value={prediction.risk_status} 
                                        isAtRisk={prediction.risk_status === 'AT-RISK'}
                                    />
                                     <ResultMetric 
                                        label="Hypothetical Status" 
                                        value={hypotheticalPrediction.risk_status} 
                                        isAtRisk={hypotheticalPrediction.risk_status === 'AT-RISK'}
                                    />
                                    <ResultMetric 
                                        label="Original Success %" 
                                        value={`${prediction.success_probability}%`}
                                    />
                                     <ResultMetric 
                                        label="Hypothetical Success %" 
                                        value={`${hypotheticalPrediction.success_probability}%`}
                                        delta={hypotheticalPrediction.success_probability - prediction.success_probability}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}