import React, { useState } from 'react';
import axios from 'axios';

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
      localStorage.setItem('waf_token', response.data.access_token);
    } catch (err) {
      setError('Invalid Username or Password');
    }
  };

  return (
    <div style={{height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#121212', color: 'white'}}>
      <form onSubmit={handleSubmit} style={{background: '#1e1e1e', padding: '40px', borderRadius: '8px', boxShadow: '0 4px 15px rgba(0,0,0,0.5)'}}>
        <h2 style={{textAlign: 'center', marginBottom: '20px'}}>AI-WAF Login</h2>
        {error && <div style={{color: '#ff4444', marginBottom: '15px', textAlign:'center'}}>{error}</div>}
        
        <div style={{marginBottom: '15px'}}>
          <label style={{display:'block', marginBottom:'5px'}}>Username</label>
          <input type="text" value={username} onChange={e => setUsername(e.target.value)} 
            style={{width: '100%', padding: '10px', borderRadius: '4px', border: 'none', background: '#333', color: 'white'}} />
        </div>
        
        <div style={{marginBottom: '20px'}}>
          <label style={{display:'block', marginBottom:'5px'}}>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} 
            style={{width: '100%', padding: '10px', borderRadius: '4px', border: 'none', background: '#333', color: 'white'}} />
        </div>
        
        <button type="submit" style={{width: '100%', padding: '10px', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight:'bold'}}>
          SECURE LOGIN
        </button>
      </form>
    </div>
  );
}

export default Login;