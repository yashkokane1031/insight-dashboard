import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // 1. Import our custom hook
import './LoginPage.css';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth(); // 2. Get the login function from our context

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');

    const loginDetails = new URLSearchParams();
    loginDetails.append('username', username);
    loginDetails.append('password', password);

    try {
      const response = await fetch('http://127.0.0.1:8000/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: loginDetails,
      });

      if (response.ok) {
        const data = await response.json();
        // 3. Instead of console.log, call the login function to save the token
        login(data.access_token);
        navigate('/'); 
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to log in.');
      }
    } catch (err) {
      setError('An error occurred. Is the backend server running?');
    }
  };

  // The JSX part of the component remains the same
  return (
    <div className="login-container">
      <div className="login-form">
        <h2>Welcome to InSight</h2>
        <p>Please sign in to continue</p>
        <form onSubmit={handleSubmit}>
            {/* ... your input fields ... */}
            <div className="input-group">
                <label htmlFor="username">Username</label>
                <input type="text" id="username" value={username} onChange={(e) => setUsername(e.target.value)} required />
            </div>
            <div className="input-group">
                <label htmlFor="password">Password</label>
                <input type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            {error && <p className="error-message">{error}</p>}
            <button type="submit" className="login-button">Sign In</button>
        </form>
      </div>
    </div>
  );
}

export default LoginPage;