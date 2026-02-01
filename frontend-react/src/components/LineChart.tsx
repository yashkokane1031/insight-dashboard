import { useEffect, useRef, useState } from 'react';
import Chart from 'chart.js/auto';
import { useWebSocketContext } from '../context/WebSocketContext';
import { useAuth } from '../context/AuthContext';

interface ForecastPoint {
    timestamp: string;
    value: number;
    lower_bound: number;
    upper_bound: number;
}

interface ForecastData {
    predicted: ForecastPoint[];
    anomalies: Array<{ timestamp: string; value: number; is_anomaly: boolean }>;
}

function LineChart() {
    const chartRef = useRef<HTMLCanvasElement>(null);
    const chartInstance = useRef<Chart | null>(null);
    const { token } = useAuth();

    // Use shared WebSocket context for real-time data
    const { history, isConnected } = useWebSocketContext();

    // Forecast state
    const [forecast, setForecast] = useState<ForecastData | null>(null);
    const [showForecast, setShowForecast] = useState(true);

    // Fetch forecast data
    const fetchForecast = async () => {
        if (!token) return;

        try {
            const response = await fetch('http://127.0.0.1:8000/data/forecast', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const data = await response.json();
                setForecast(data);
            }
        } catch (error) {
            console.error('Error fetching forecast:', error);
        }
    };

    // Fetch forecast periodically (every 30 seconds)
    useEffect(() => {
        if (token && history.length >= 10) {
            fetchForecast();
            const interval = setInterval(fetchForecast, 30000);
            return () => clearInterval(interval);
        }
    }, [token, history.length]);

    // Initialize Chart.js instance
    useEffect(() => {
        if (chartRef.current) {
            chartInstance.current = new Chart(chartRef.current, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Actual',
                            data: [],
                            borderColor: '#3182CE',
                            backgroundColor: 'rgba(49, 130, 206, 0.1)',
                            fill: true,
                            tension: 0.4,
                            pointRadius: 2
                        },
                        {
                            label: 'Predicted',
                            data: [],
                            borderColor: '#9F7AEA',
                            borderDash: [5, 5],
                            backgroundColor: 'transparent',
                            fill: false,
                            tension: 0.4,
                            pointRadius: 3,
                            pointStyle: 'triangle'
                        },
                        {
                            label: 'Anomalies',
                            data: [],
                            borderColor: '#F56565',
                            backgroundColor: '#F56565',
                            fill: false,
                            pointRadius: 8,
                            pointStyle: 'crossRot',
                            showLine: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: false, suggestedMin: 40, suggestedMax: 90 },
                        x: { display: true }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: { usePointStyle: true }
                        }
                    },
                    animation: { duration: 300 }
                }
            });
        }
        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, []);

    // Update chart when history or forecast changes
    useEffect(() => {
        if (chartInstance.current && history.length > 0) {
            // Actual data
            const actualLabels = history.map(item => new Date(item.timestamp).toLocaleTimeString());
            const actualValues = history.map(item => item.value);

            // Combined labels (actual + forecast)
            let allLabels = [...actualLabels];
            let forecastValues: (number | null)[] = new Array(actualValues.length).fill(null);
            let anomalyData: (number | null)[] = new Array(actualValues.length).fill(null);

            // Add forecast data if available and enabled
            if (showForecast && forecast?.predicted) {
                const forecastLabels = forecast.predicted.map(p => new Date(p.timestamp).toLocaleTimeString());
                allLabels = [...actualLabels, ...forecastLabels];

                // Pad actual values for forecast section
                const paddedActual = [...actualValues, ...new Array(forecast.predicted.length).fill(null)];

                // Create forecast line (null for actual data points, values for forecast)
                forecastValues = [
                    ...new Array(actualValues.length - 1).fill(null),
                    actualValues[actualValues.length - 1], // Connect to last actual point
                    ...forecast.predicted.map(p => p.value)
                ];

                chartInstance.current.data.datasets[0].data = paddedActual;
            } else {
                chartInstance.current.data.datasets[0].data = actualValues;
            }

            // Add anomaly markers
            if (forecast?.anomalies) {
                const anomalyMap = new Map(forecast.anomalies.map(a => [a.timestamp, a.value]));
                anomalyData = history.map(item =>
                    anomalyMap.has(item.timestamp) ? item.value : null
                );
            }

            chartInstance.current.data.labels = allLabels;
            chartInstance.current.data.datasets[1].data = forecastValues;
            chartInstance.current.data.datasets[2].data = anomalyData;
            chartInstance.current.update('none');
        }
    }, [history, forecast, showForecast]);

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h2 style={{ margin: 0 }}>
                    History
                    <span style={{
                        marginLeft: '10px',
                        fontSize: '0.7rem',
                        color: isConnected ? '#48BB78' : '#F56565',
                        fontWeight: 'normal'
                    }}>
                        {isConnected ? '● LIVE' : '○ OFFLINE'}
                    </span>
                </h2>
                <label style={{ fontSize: '0.85rem', color: '#A0AEC0', cursor: 'pointer' }}>
                    <input
                        type="checkbox"
                        checked={showForecast}
                        onChange={(e) => setShowForecast(e.target.checked)}
                        style={{ marginRight: '6px' }}
                    />
                    Show Forecast
                </label>
            </div>
            <div style={{ position: 'relative', height: '300px', width: '600px' }}>
                <canvas ref={chartRef}></canvas>
            </div>
            {forecast && (
                <div style={{ fontSize: '0.75rem', color: '#718096', marginTop: '8px' }}>
                    Forecast: {forecast.predicted.length} points |
                    Anomalies detected: {forecast.anomalies?.length || 0}
                </div>
            )}
        </div>
    );
}

export default LineChart;