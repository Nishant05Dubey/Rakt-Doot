import { useState, useEffect } from 'react';
import Header from '../components/Header';
import { Activity } from 'lucide-react';
import './LiveFeed.css';

export default function LiveFeed() {
  const [feed, setFeed] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        if (!apiUrl) return;
        const res = await fetch(`${apiUrl}/admin/dashboard`);
        if (res.ok) {
          const data = await res.json();
          if (data.live_feed) setFeed(data.live_feed);
        }
      } catch (err) {
        console.error('Failed to fetch live feed', err);
      }
    };
    fetchData();
  }, []);

  const getBadge = (type) => {
    switch(type) {
      case 'ai': return <span className="feed-badge ai-badge">AI</span>;
      case 'msg': return <span className="feed-badge msg-badge">MSG</span>;
      case 'ok': return <span className="feed-badge ok-badge">OK</span>;
      default: return null;
    }
  };

  return (
    <div className="animate-fade-in">
      <Header title="Live Coordination Feed" subtitle="AI ACTIVITY STREAM" />
      
      <div className="card feed-container">
        <div className="feed-header">
          <div>
            <h3 className="text-h2" style={{fontSize: '1.125rem'}}>Live AI Activity Feed</h3>
            <div className="text-muted" style={{fontSize: '0.875rem'}}>Real-time stream from coordination engine</div>
          </div>
          <div className="status-live">● LIVE</div>
        </div>

        <div className="feed-list">
          {feed.length === 0 ? <div className="text-muted">Waiting for AI engine events...</div> :
            feed.map((evt, i) => (
            <div key={i} className="feed-item">
              <div className="feed-timeline-line" style={{ display: i === feed.length - 1 ? 'none' : 'block' }}></div>
              <div className="feed-dot"></div>
              <div className="feed-content">
                <div className="feed-meta">
                  {getBadge(evt.type)}
                  <span className="feed-time">{evt.time}</span>
                </div>
                <div className="feed-text">{evt.text}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
