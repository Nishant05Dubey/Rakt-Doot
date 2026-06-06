import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, Activity, Rss, Settings, Droplet } from 'lucide-react';
import './Sidebar.css';

export default function Sidebar() {
  const navItems = [
    { icon: <LayoutDashboard size={20} />, label: 'Overview', path: '/' },
    { icon: <Users size={20} />, label: 'Patients', path: '/patients' },
    { icon: <Activity size={20} />, label: 'Donor Pods', path: '/donor-pods' },
    { icon: <Rss size={20} />, label: 'Live Feed', path: '/live-feed' },
    { icon: <Settings size={20} />, label: 'Settings', path: '/settings' },
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="logo-icon">
          <Droplet fill="#e11d48" color="#e11d48" size={24} />
        </div>
        <div className="brand-text">
          <h1 className="brand-title">रक्त Doot</h1>
          <span className="brand-subtitle">BLOOD BRIDGE</span>
        </div>
      </div>

      <nav className="nav-menu">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="org-profile">
          <div className="org-avatar">LF</div>
          <div className="org-info">
            <div className="org-name">LifeBlood Foundation</div>
            <div className="org-status">NGO · Verified</div>
          </div>
        </div>
        <div className="powered-by">POWERED BY RAKT DOOT AI</div>
      </div>
    </aside>
  );
}
