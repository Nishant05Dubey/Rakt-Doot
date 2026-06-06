import './Header.css';

export default function Header({ title, subtitle }) {
  return (
    <header className="page-header">
      <div className="header-content">
        <div className="header-titles">
          {subtitle && <span className="text-subtitle">{subtitle}</span>}
          <h2 className="text-h1">{title}</h2>
        </div>
        <div className="header-status">
          <div className="status-indicator">
            <span className="status-dot"></span>
            <span className="status-text">STATUS<br/><b>All Systems Nominal</b></span>
          </div>
          <div className="user-avatar">LF</div>
        </div>
      </div>
      <div className="ekg-line"></div>
    </header>
  );
}
