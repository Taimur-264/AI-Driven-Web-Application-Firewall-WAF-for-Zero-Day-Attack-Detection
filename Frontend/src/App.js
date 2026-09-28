import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaHome, FaChartBar, FaCog, FaUserShield, FaFileDownload } from 'react-icons/fa';
import './App.css'; 

// --- LOGIN COMPONENT ---
function Login({ setToken }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:8000/token', {
        username,
        password
      });
      setToken(response.data.access_token);
      sessionStorage.setItem('waf_token', response.data.access_token);
    } catch (err) {
      setError('Invalid Username or Password');
    }
  };

  return (
    <div style={{height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#121212', color: 'white'}}>
      <form onSubmit={handleSubmit} style={{background: '#1e1e1e', padding: '40px', borderRadius: '8px', boxShadow: '0 4px 15px rgba(0,0,0,0.5)', width: '300px'}}>
        <h2 style={{textAlign: 'center', marginBottom: '20px', color: '#007bff'}}>AI-WAF Login</h2>
        {error && <div style={{color: '#ff4444', marginBottom: '15px', textAlign:'center', fontSize:'14px'}}>{error}</div>}
        
        <div style={{marginBottom: '15px'}}>
          <label style={{display:'block', marginBottom:'5px', fontSize:'14px'}}>Username</label>
          <input type="text" value={username} onChange={e => setUsername(e.target.value)} 
            style={{width: '90%', padding: '10px', borderRadius: '4px', border: '1px solid #333', background: '#333', color: 'white'}} />
        </div>
        
        <div style={{marginBottom: '20px'}}>
          <label style={{display:'block', marginBottom:'5px', fontSize:'14px'}}>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} 
            style={{width: '90%', padding: '10px', borderRadius: '4px', border: '1px solid #333', background: '#333', color: 'white'}} />
        </div>
        
        <button type="submit" style={{width: '100%', padding: '10px', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight:'bold'}}>
          SECURE LOGIN
        </button>
      </form>
    </div>
  );
}

// --- MAIN DASHBOARD COMPONENT ---
function App() {
  const [token, setToken] = useState(sessionStorage.getItem('waf_token'));
  
  const [data, setData] = useState({
    kpi: { total: 0, blocked: 0, allowed: 0, score: 100 },
    monitor: { rps: 0, block_rate: 0, avg_response: 18 },
    threats: {}, 
    events: [],
    system: { cpu: 0, memory: 0, disk: 0, network: 0 }
  });

  const handleLogout = () => {
    setToken(null);
    sessionStorage.removeItem('waf_token'); 
  };

  const handleReport = () => {
      alert("Generating Security Report (PDF)... \n[Simulated for Defense Demo]");
  };

  const handleSettings = () => {
      alert("Opening Configuration Panel... \n[Restricted to Super-Admin]");
  };

  // 1. DATA MAPPING FIX: Properly unpack the new backend data format
  useEffect(() => {
    if (!token) return;
    const fetchStats = setInterval(() => {
      axios.get('http://127.0.0.1:8000/api/v1/stats', {
          headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => {
          const logs = res.data.logs || [];
          
          // Aggregate threats for the bar chart based on the new XAI format
          const threatCounts = {};
          logs.forEach(log => {
              // Extract base threat name (e.g., 'OWASP A03' or 'AI Anomaly') from the XAI string
              const baseName = log.reason.split(" - ")[0]; 
              threatCounts[baseName] = (threatCounts[baseName] || 0) + 1;
          });

          setData(prev => {
              // Simulate total traffic continuing to grow for demo purposes
              const newTotal = prev.kpi.total > logs.length ? prev.kpi.total + Math.floor(Math.random() * 3) : logs.length * 2 + 10;
              
              return {
                  ...prev,
                  kpi: { 
                      total: newTotal,
                      blocked: logs.length, 
                      allowed: newTotal - logs.length, 
                      score: logs.length > 20 ? 45 : (logs.length > 5 ? 80 : 100) 
                  },
                  monitor: {
                      rps: Math.floor(Math.random() * 15) + 5,
                      block_rate: newTotal > 0 ? Math.floor((logs.length / newTotal) * 100) : 0,
                      avg_response: Math.floor(Math.random() * 5) + 12
                  },
                  threats: threatCounts,
                  events: logs // Directly pass the Python array to the React view
              };
          });
      })
      .catch(err => console.log("Connecting..."));
    }, 1000);
    return () => clearInterval(fetchStats);
  }, [token]);

  const getThreatPercent = (val) => {
    if (data.kpi.blocked === 0) return 0;
    return Math.round((val / data.kpi.blocked) * 100);
  };

  if (!token) {
    return <Login setToken={setToken} />;
  }

  return (
    <div className="App">
      <header className="header">
        <div style={{fontWeight:'bold', fontSize: 18, display:'flex', alignItems:'center', gap:'10px'}}>
            <FaUserShield /> AI-WAF DASHBOARD
        </div>
        <div className="nav">
            <div className="nav-item"><FaHome /> Home</div>
            <div className="nav-item" onClick={handleReport} style={{cursor:'pointer'}}><FaFileDownload /> Reports</div>
            <div className="nav-item" onClick={handleSettings} style={{cursor:'pointer'}}><FaCog /> Settings</div>
        </div>
        <div className="user-info">
            <span style={{marginRight: 10, fontSize:14}}>[Status: LIVE]</span>
            <button onClick={handleLogout} style={{background: '#cc0000', color: 'white', border: 'none', padding: '5px 15px', cursor: 'pointer', borderRadius: '4px', fontWeight:'bold'}}>
              Logout
            </button>
        </div>
      </header>

      <div className="container">
        
        {/* KPI CARDS */}
        <div className="kpi-row">
            <StatsCard title="Total Requests" val={data.kpi.total} sub="Live Counter" color="green" />
            <StatsCard title="Blocked Requests" val={data.kpi.blocked} sub="Attacks Stopped" color="red" />
            <StatsCard title="Allowed Requests" val={data.kpi.allowed} sub="Safe Traffic" color="green" />
            <div className="card">
                <h3>Threat Score</h3>
                <h1 className={data.kpi.score > 80 ? "green" : "red"}>{data.kpi.score}/100</h1>
                <div className="stat-sub">{data.kpi.score > 80 ? "System Secure" : "Under Attack"}</div>
            </div>
        </div>

        {/* MONITOR */}
        <div className="monitor-card">
            <div className="section-title">Real-Time Traffic Monitor</div>
            <BarRow label="Requests/Second:" val={data.monitor.rps} max={100} unit="RPS" color="#00aa00" />
            <BarRow label="Block Rate:" val={data.monitor.block_rate} max={100} unit="%" color="#cc0000" />
            <BarRow label="Avg Response:" val={data.monitor.avg_response} max={50} unit="ms" color="#0066cc" />
        </div>

        {/* BOTTOM SECTION */}
        <div className="bottom-row">
            
            {/* THREATS */}
            <div className="card" style={{textAlign:'left'}}>
                <div className="section-title">TOP THREATS (OWASP & AI)</div>
                {Object.keys(data.threats).length === 0 ? (
                    <div style={{padding:20, color:'#888', textAlign:'center'}}>No threats detected yet...</div>
                ) : (
                    Object.entries(data.threats).map(([name, count]) => (
                        <ThreatBar key={name} name={name} val={getThreatPercent(count)} count={count} color="#cc0000" />
                    ))
                )}
            </div>

            {/* EVENTS - XAI FIX: Updated to display the new Explanable AI Evidence correctly */}
            <div className="card" style={{textAlign:'left', overflowY: 'auto', maxHeight: '300px'}}>
                <div className="section-title">RECENT XAI EVENTS</div>
                {data.events.length === 0 ? (
                    <div style={{padding:20, color:'#888', textAlign:'center'}}>Waiting for traffic...</div>
                ) : (
                    data.events.map((e, i) => (
                        <div key={i} className="event-item" style={{ borderBottom: '1px solid #333', padding: '10px 0' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                                <span className="event-time" style={{ color: '#888', fontSize: '12px' }}>{e.timestamp}</span>
                                <span style={{ color: '#cc0000', fontWeight: 'bold', fontSize: '12px', background: '#330000', padding: '2px 6px', borderRadius: '4px' }}>BLOCKED</span>
                            </div>
                            {/* XAI Evidence String Displayed Here */}
                            <div style={{ fontWeight: 'bold', color: '#ffcc00', marginBottom: '3px', fontSize: '14px' }}>{e.reason}</div>
                            {/* Technical Details Displayed Here */}
                            <div style={{ fontSize: '11px', color: '#aaa', wordBreak: 'break-all' }}>IP: {e.ip} | Payload: {e.payload}</div>
                        </div>
                    ))
                )}
            </div>
        </div>

        {/* FOOTER */}
        <div className="system-footer">
            <span>SYSTEM METRICS</span>
            <span>CPU: <span style={{color:'green'}}>{Math.floor(Math.random() * 10) + 2}%</span></span>
            <span>Memory: <span style={{color:'#0066cc'}}>{Math.floor(Math.random() * 5) + 40}%</span></span>
            <span>Network: <span style={{color:'green'}}>{Math.floor(Math.random() * 3) + 1} MB/s ▲</span></span>
        </div>

      </div>
    </div>
  );
}

// Sub-components
const StatsCard = ({title, val, sub, color}) => (
    <div className="card">
        <h3>{title}</h3>
        <h1>{val.toLocaleString()}</h1>
        <div className={`stat-sub ${color}`}>{sub}</div>
    </div>
);

const BarRow = ({label, val, max, unit, color}) => (
    <div className="bar-row">
        <div className="bar-label">{label}</div>
        <div className="bar-track">
            <div className="bar-fill" style={{width: `${Math.min((val/max)*100, 100)}%`, background: color}}></div>
        </div>
        <div>{val} {unit}</div>
    </div>
);

const ThreatBar = ({name, val, count, color}) => (
    <div className="threat-row">
        <div style={{width:100, fontWeight:'bold', fontSize:12}}>• {name}</div>
        <div style={{fontSize:12, fontWeight:'bold', marginRight:10, width: 30}}>{count}</div>
        <div className="bar-track" style={{height:10, width:150, margin:0}}>
             <div className="bar-fill" style={{width: `${val}%`, background: color}}></div>
        </div>
    </div>
);

export default App;