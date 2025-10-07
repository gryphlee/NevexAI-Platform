// src/app/page.js
"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation'; // NEW: Import the router

export default function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState(null);
  
  const router = useRouter(); // NEW: Initialize the router

  useEffect(() => {
    // ... (fetchStats logic remains the same)
    const fetchStats = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/dashboard-stats');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch dashboard stats:", error);
      }
    };
    fetchStats();
  }, []);

  // --- MODIFIED: Updated Login Logic ---
  const handleLoginSubmit = async (event) => {
    event.preventDefault();
    setError('');

    const form = event.target;
    const formData = new FormData();
    formData.append('username', form.username.value);
    formData.append('password', form.password.value);
    
    try {
      // We now call the /token endpoint which is designed for this purpose
      const response = await fetch('http://127.0.0.1:8000/token', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        
        // On success, we get an access token. Save to localStorage and cookie (fallback across tabs/origins).
        localStorage.setItem('accessToken', data.access_token);
        try {
          document.cookie = `accessToken=${encodeURIComponent(data.access_token)}; path=/; max-age=2592000`;
        } catch {}
        
        // Close the modal
        setIsModalOpen(false);
        
        // Redirect to the dashboard page
        router.push('/dashboard'); 

      } else {
        // Handle failed login
        const errorData = await response.json();
        setError(errorData.detail || 'Invalid username or password.');
      }
    } catch (err) {
      console.error('Login Error:', err);
      setError('A connection error occurred. Is the backend running?');
    }
  };

  return (
    <>
      {/* The rest of your JSX remains exactly the same as before */}
      {/* ===== NEURAL BACKGROUND ===== */}
      <div className="neural-bg">
        <div className="neural-node" style={{ top: '10%', left: '20%' }}></div>
        <div className="neural-node" style={{ top: '30%', left: '70%' }}></div>
        <div className="neural-node" style={{ top: '60%', left: '40%' }}></div>
        <div className="neural-node" style={{ top: '80%', left: '80%' }}></div>
        <div className="neural-connection" style={{ top: '15%', left: '20%', width: '50%', transform: 'rotate(25deg)' }}></div>
        <div className="neural-connection" style={{ top: '65%', left: '40%', width: '40%', transform: 'rotate(-15deg)' }}></div>
      </div>

      {/* ===== NAVIGATION ===== */}
      <nav>
        <div className="logo-container">
          <div className="logo-icon">⚡</div>
          <div className="logo-text">
            <span>NEVEX</span> AI
            <span className="nav-badge">Multi-Agent System</span>
          </div>
        </div>
        <button className="nav-cta" onClick={() => setIsModalOpen(true)}>
          Log In / Request Demo
        </button>
      </nav>

      <main>
        <section className="hero">
            <div className="hero-left">
                <div className="hero-badge">
                    <span className="pulse-dot"></span>
                    20+ Autonomous Agents Working in Real-Time
                </div>
                <h1>
                    The First <span className="highlight">AI Student Intervention Platform</span> Powered by Autonomous Agent Coordination
                </h1>
                <p className="hero-subtitle">
                    Nevex AI deploys 20+ specialized agents that detect, debate, and execute personalized interventions for at-risk students—before they fail. Think medical team consultation, but for education.
                </p>
                <div className="hero-stats">
                    <div className="stat-item">
                        <div className="stat-number">{stats ? `${stats.successRate}%` : '...'}</div>
                        <div className="stat-label">Recovery Rate</div>
                    </div>
                    <div className="stat-item">
                        <div className="stat-number">{stats ? stats.interventionSpeed : '...'}</div>
                        <div className="stat-label">Weeks to Intervene</div>
                    </div>
                    <div className="stat-item">
                        <div className="stat-number">{stats ? `${stats.agentSuccessRate}%` : '...'}</div>
                        <div className="stat-label">Agent Success Rate</div>
                    </div>
                </div>
                <div className="hero-buttons">
                    <button className="btn-primary">See System Live</button>
                    <button className="btn-secondary">How It Works →</button>
                </div>
            </div>
            <div className="hero-right">
                <div className="dashboard-preview">
                    <div className="mini-chart">
                      <div className="chart-title">Success Rate</div>
                      <div className="chart-big-number">{stats ? `${stats.successRate}%` : '...'}</div>
                      <div className="chart-label">Students Recovered</div>
                      <div className="chart-visual">
                          <div className="progress-bar">
                              <div className="progress-fill" style={{ width: stats ? `${stats.successRate}%` : '0%' }}></div>
                          </div>
                      </div>
                    </div>

                    <div className="mini-chart">
                        <div className="chart-title">Intervention Speed</div>
                        <div className="chart-big-number">{stats ? stats.interventionSpeed : '...'}</div>
                        <div className="chart-label">Weeks (50% faster)</div>
                        <div className="chart-visual">
                            <div className="mini-bars">
                                <div className="bar" style={{ height: '80%' }}></div>
                                <div className="bar" style={{ height: '50%' }}></div>
                                <div className="bar" style={{ height: '40%' }}></div>
                                <div className="bar" style={{ height: '35%' }}></div>
                            </div>
                        </div>
                    </div>

                    <div className="mini-chart">
                        <div className="chart-title">Agent Performance</div>
                        <div className="chart-big-number">{stats ? stats.agentPerformance.activeAgents : '...'}</div>
                        <div className="chart-label">Specialized Agents Active</div>
                        <div className="chart-visual">
                            <div className="agent-grid">
                                <div className="agent-cell">Math {stats ? stats.agentPerformance.specializations.math : '..'}%</div>
                                <div className="agent-cell">Empathy {stats ? stats.agentPerformance.specializations.empathy : '..'}%</div>
                                <div className="agent-cell">Data {stats ? stats.agentPerformance.specializations.data : '..'}%</div>
                                <div className="agent-cell">Resource {stats ? stats.agentPerformance.specializations.resource : '..'}%</div>
                            </div>
                        </div>
                    </div>

                    <div className="mini-chart">
                        <div className="chart-title">Detection vs Manual</div>
                        <div className="chart-big-number">{stats ? stats.detectionVsManual : '...'}</div>
                        <div className="chart-label">Faster Than Traditional</div>
                        <div className="chart-visual">
                            <div className="mini-bars">
                                <div className="bar" style={{ height: '90%' }}></div>
                                <div className="bar" style={{ height: '70%' }}></div>
                                <div className="bar" style={{ height: '45%' }}></div>
                                <div className="bar" style={{ height: '15%' }}></div>
                            </div>
                        </div>
                    </div>

                    <div className="mini-chart">
                        <div className="chart-title">Multi-Agent Debates</div>
                        <div className="chart-big-number">{stats ? stats.multiAgentDebates : '...'}</div>
                        <div className="chart-label">Debates This Week</div>
                        <div className="chart-visual">
                            <div className="progress-bar">
                                <div className="progress-fill" style={{ width: '92%' }}></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section className="identity-section">
            <h2>Powered by Multi-Agent Intelligence</h2>
            <p className="subtitle">Not a single AI. A coordinated swarm of specialized agents.</p>
            <div className="identity-grid">
              <div className="identity-card">
                  <div className="identity-icon">🎯</div>
                  <h3>Student Intervention First</h3>
                  <p>Built specifically to detect and prevent student failure through early intervention. Every feature exists to save at-risk students before it's too late.</p>
              </div>
              <div className="identity-card">
                  <div className="identity-icon">💭</div>
                  <h3>Multi-Agent Debate System</h3>
                  <p>20+ specialized agents compete and debate optimal strategies. Like a medical consultation team—multiple expert perspectives eliminate bias.</p>
              </div>
              <div className="identity-card">
                  <div className="identity-icon">🧬</div>
                  <h3>Self-Evolving Agents</h3>
                  <p>Agents compete through Darwinian selection. High performers reproduce with mutations. Low performers are deprecated. The system improves itself autonomously.</p>
              </div>
            </div>
        </section>

        <section className="architecture-section">
            <h2>How the Swarm Operates</h2>
            <div className="architecture-flow">
              <div className="flow-step">
                  <div className="flow-number">1</div>
                  <h3>Detect</h3>
                  <p>Watcher Agent continuously monitors all students, detecting invisible patterns in grades, engagement, and behavior.</p>
              </div>
              <div className="flow-step">
                  <div className="flow-number">2</div>
                  <h3>Debate</h3>
                  <p>Top 3 agents compete to handle the case, then engage in multi-round argumentation to find optimal strategy.</p>
              </div>
              <div className="flow-step">
                  <div className="flow-number">3</div>
                  <h3>Execute</h3>
                  <p>Task Force coordinates personalized outreach, resources, and follow-ups—adapting in real-time based on response.</p>
              </div>
            </div>
        </section>

        <section className="testimonials-section">
            <h2>Deployed at Leading Institutions</h2>
            <div className="testimonials-grid">
              <div className="testimonial-card">
                  <div className="testimonial-header">
                      <div className="testimonial-avatar">MR</div>
                      <div className="testimonial-author">
                          <h4>Maria Rodriguez</h4>
                          <p>Academic Coordinator, San Pedro Academy</p>
                      </div>
                  </div>
                  <p className="testimonial-text">"The debate transcripts are incredible—I can see WHY the AI made each recommendation. It's like having 5 expert consultants for every at-risk student."</p>
                  <div className="testimonial-metric">
                      <div className="number">+23%</div>
                      <div className="label">Recovery Rate Increase</div>
                  </div>
              </div>
              <div className="testimonial-card">
                  <div className="testimonial-header">
                      <div className="testimonial-avatar">JC</div>
                      <div className="testimonial-author">
                          <h4>Dr. James Chen</h4>
                          <p>Department Head, Ateneo de Manila</p>
                      </div>
                  </div>
                  <p className="testimonial-text">"Agent #7's empathy-first approach identified patterns I completely missed. The system caught login time anomalies and message tone changes that indicated home issues."</p>
                  <div className="testimonial-metric">
                      <div className="number">87%</div>
                      <div className="label">Early Detection Accuracy</div>
                  </div>
              </div>
              <div className="testimonial-card">
                  <div className="testimonial-header">
                      <div className="testimonial-avatar">AL</div>
                      <div className="testimonial-author">
                          <h4>Anna Lopez</h4>
                          <p>Principal, Manila Science High School</p>
                      </div>
                  </div>
                  <p className="testimonial-text">"The ability to coordinate multiple intervention strategies simultaneously is game-changing. We saw measurable improvements within 3 weeks of deployment."</p>
                  <div className="testimonial-metric">
                      <div className="number">20 hrs</div>
                      <div className="label">Weekly Time Saved</div>
                  </div>
              </div>
            </div>
        </section>

        <section className="final-cta">
            <h2>Stop Reacting to Failure.<br/>Start Preventing It.</h2>
            <p>Join forward-thinking schools using swarm intelligence to transform outcomes.</p>
            <button className="btn-primary">Schedule Discovery Call</button>
        </section>
        
        <footer>
            <p>© 2025 <span className="footer-highlight">Nevex AI</span> - Autonomous Student Intervention Platform</p>
            <p>Powered by multi-agent swarm intelligence with Darwinian evolution</p>
        </footer>
      </main>

      {/* ===== LOGIN MODAL ===== */}
      {isModalOpen && (
        <div 
          className="modal-overlay" 
          style={{ display: 'flex' }}
          onClick={(e) => { if(e.target === e.currentTarget) setIsModalOpen(false); }}
        >
          <div className="login-modal">
            <h2>Platform Login</h2>
            <form onSubmit={handleLoginSubmit}>
              <input type="text" name="username" placeholder="Username" required />
              <input type="password" name="password" placeholder="Password" required />
              <button type="submit">Log In</button>
            </form>
            {error && <p className="error-message" style={{ display: 'block' }}>{error}</p>}
          </div>
        </div>
      )}
    </>
  );
}
