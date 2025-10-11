import RealtimeValue from './components/RealtimeValue';
import LineChart from './components/LineChart';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import './index.css';

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <Sidebar />
      <main className="content-area">
        <h1 style={{ textAlign: 'center' }}>InSight Dashboard</h1>
        
        {/* This div uses Flexbox to perfectly center the charts */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          gap: '2rem', 
          flexWrap: 'wrap', 
          alignItems: 'center' 
        }}>
          <RealtimeValue/>
          <LineChart />
        </div>
      </main>
    </div>
  );
}

export default App;