import { useState, useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import { useAuth } from '../context/AuthContext';

function GaugeChart() {
  const [value, setValue] = useState<number | null>(null);
  const { token } = useAuth();
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (chartRef.current) {
      chartInstance.current = new Chart(chartRef.current, {
        type: 'doughnut',
        data: {
          labels: ['Temp', ''],
          datasets: [{
            data: [0, 100],
            backgroundColor: ['#3182CE', 'rgba(201, 203, 207, 0.2)'],
            circumference: 180,
            rotation: 270,
          }]
        },
        options: {
          responsive: true,
          cutout: '80%',
          plugins: {
            legend: { display: false },
            tooltip: { enabled: false }
          }
        }
      });
    }
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, []);

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
              if (chartInstance.current) {
                chartInstance.current.data.datasets[0].data[0] = data.value;
                chartInstance.current.data.datasets[0].data[1] = 100 - data.value;
                chartInstance.current.update();
              }
            }
          })
          .catch(error => console.error('Error fetching gauge data:', error));
      };

      fetchData();
      const intervalId = setInterval(fetchData, 3000);
      return () => clearInterval(intervalId);
    }
  }, [token]);

  return (
    <div style={{
      width: '600px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '0'
    }}>
      <h2 style={{ marginBottom: '0' }}>CPU Temperature</h2>
      <div style={{
        position: 'relative',
        width: '300px',
        height: '150px'
      }}>
        <canvas ref={chartRef}></canvas>
        {typeof value === 'number' ? (
          <p style={{
            margin: 0,
            fontSize: '3rem',
            fontWeight: 'bold',
            position: 'absolute',
            top: '55%',
            left: '50%',
            transform: 'translate(-50%, -50%)'
          }}>
            {value.toFixed(2)}°C
          </p>
        ) : (
          <p style={{
            margin: 0,
            fontSize: '1.5rem',
            position: 'absolute',
            top: '55%',
            left: '50%',
            transform: 'translate(-50%, -50%)'
          }}>
            {token ? "Loading..." : "Please log in"}
          </p>
        )}
      </div>
    </div>
  );
}

export default GaugeChart;