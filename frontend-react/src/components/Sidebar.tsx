import './Sidebar.css';

function Sidebar() {
  return (
    <aside className="sidebar">
      <ul className="sidebar-nav">
        <li className="nav-item active">Dashboard</li>
        <li className="nav-item">Alerts</li>
        <li className="nav-item">Settings</li>
      </ul>
    </aside>
  );
}

export default Sidebar;