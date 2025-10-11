import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import { useAuth } from '../context/AuthContext';

function LineChart() {
    const chartRef = useRef<HTMLCanvasElement>(null);
    const chartInstance = useRef<Chart | null>(null);
    const { token } = useAuth();

    useEffect(() => {
        if (chartRef.current) {
            chartInstance.current = new Chart(chartRef.current, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU Temperature History',
                        data: [],
                        borderColor: '#3182CE',
                        backgroundColor: (context) => {
                            const ctx = context.chart.ctx;
                            if (!ctx) return 'transparent';
                            const gradient = ctx.createLinearGradient(0, 0, 0, 250);
                            gradient.addColorStop(0, 'rgba(49, 130, 206, 0.5)');
                            gradient.addColorStop(1, 'rgba(49, 130, 206, 0)');
                            return gradient;
                        },
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                   scales: { y: { beginAtZero: false, suggestedMin: 40, suggestedMax: 90 } },
                   plugins: { legend: { display: false } }
                }
            });
        }
         return () => { if (chartInstance.current) { chartInstance.current.destroy(); }};
    }, []);

    useEffect(() => {
        if (token) {
            const fetchData = () => {
                fetch('http://127.0.0.1:8000/data/history', {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
                .then(response => response.ok ? response.json() : Promise.reject('Auth failed'))
                .then((data: {timestamp: string, value: number}[]) => {
                    if (chartInstance.current && data) {
                        const labels = data.map(item => new Date(item.timestamp).toLocaleTimeString());
                        const values = data.map(item => item.value);
                        chartInstance.current.data.labels = labels;
                        chartInstance.current.data.datasets[0].data = values;
                        chartInstance.current.update();
                    }
                })
                .catch(error => console.error('Error fetching history:', error));
            };
            fetchData();
            const intervalId = setInterval(fetchData, 3000);
            return () => clearInterval(intervalId);
        }
    }, [token]);

    return (
        <div>
            <h2 style={{ textAlign: 'center' }}>History</h2>
            <div style={{ position: 'relative', height: '300px', width: '600px' }}>
                <canvas ref={chartRef}></canvas>
            </div>
        </div>
    );
}

export default LineChart;