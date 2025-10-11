import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

function RealtimeValue() {
  const [value, setValue] = useState<number | null>(null);
  const { token } = useAuth();

  useEffect(() => {
    if (token) {
      const fetchData = () => {
        fetch('http://127.0.0.1:8000/data/latest', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(response => response.ok ? response.json() : Promise.reject('Auth failed'))
        .then(data => {
          if (data) {
            setValue(data.value);
          }
        })
        .catch(error => console.error('Error fetching real-time value:', error));
      };

      fetchData();
      const intervalId = setInterval(fetchData, 3000);
      return () => clearInterval(intervalId);
    }
  }, [token]);

  return (
    <div style={{ width: '600px', textAlign: 'center' }}>
      <h2>CPU Temperature</h2>
      <div style={{ fontSize: '6rem', fontWeight: 'bold', margin: '2rem 0' }}>
        {typeof value === 'number' ? `${value.toFixed(2)}°C` : 'Loading...'}
      </div>
    </div>
  );
}

export default RealtimeValue;