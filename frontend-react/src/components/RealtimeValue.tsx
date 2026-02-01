import { useWebSocketContext } from '../context/WebSocketContext';

function RealtimeValue() {
  // Use shared WebSocket context for real-time data
  const { latestValue, isConnected } = useWebSocketContext();

  return (
    <div style={{ width: '600px', textAlign: 'center' }}>
      <h2>
        CPU Temperature
        <span style={{
          marginLeft: '10px',
          fontSize: '0.7rem',
          color: isConnected ? '#48BB78' : '#F56565',
          fontWeight: 'normal'
        }}>
          {isConnected ? '● LIVE' : '○ OFFLINE'}
        </span>
      </h2>
      <div style={{ fontSize: '6rem', fontWeight: 'bold', margin: '2rem 0' }}>
        {latestValue ? `${latestValue.value.toFixed(2)}°C` : 'Loading...'}
      </div>
      {latestValue && (
        <div style={{ fontSize: '0.9rem', color: '#718096' }}>
          Last updated: {new Date(latestValue.timestamp).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}

export default RealtimeValue;