import { useState, useEffect } from 'react';
import Header from '../components/Header';
import { Globe, Send } from 'lucide-react';
import './DonorPods.css';

export default function DonorPods() {
  const [pods, setPods] = useState([]);
  const [matches, setMatches] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        if (!apiUrl) return;
        const res = await fetch(`${apiUrl}/admin/dashboard`);
        if (res.ok) {
          const data = await res.json();
          if (data.pods_data) setPods(data.pods_data);
          if (data.matches) setMatches(data.matches);
        }
      } catch (err) {
        console.error('Failed to fetch donor pods', err);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="animate-fade-in">
      <Header title="Donor Pods Network" subtitle="GEOGRAPHIC CLUSTERS" />
      
      <div className="pods-grid">
        {pods.length === 0 ? <div className="p-4 text-muted">Loading live network data...</div> : 
          pods.map((pod, i) => (
          <div key={i} className="pod-card">
            <div className="pod-header">
              <div>
                <div className="pod-label">DONOR POD</div>
                <div className="pod-name">{pod.name}</div>
              </div>
              <div className="pod-icon-wrapper">
                <Globe size={18} className="pod-icon" />
              </div>
            </div>
            
            <div className="pod-stats">
              <div className="stat-box">
                <div className="stat-label">TOTAL DONORS</div>
                <div className="stat-val">{pod.total}</div>
              </div>
              <div className="stat-box">
                <div className="stat-label">ELIGIBLE NOW</div>
                <div className="stat-val text-green">{pod.eligible}</div>
              </div>
            </div>
            
            <div className="pod-reliability">
              <div className="r-header">
                <span>AI Reliability Score</span>
                <span>{pod.score}%</span>
              </div>
              <div className="r-bar-bg">
                <div className="r-bar-fill" style={{ width: `${pod.score}%` }}></div>
              </div>
            </div>
            
            <button className="btn-broadcast">
              <Send size={14} /> Broadcast Emergency Need
            </button>
          </div>
        ))}
      </div>

      <div className="card matches-section mt-6">
        <div className="matches-header">
          <div>
            <h3 className="text-h2" style={{fontSize: '1.125rem'}}>Active Donor-Patient Matches</h3>
            <div className="text-muted" style={{fontSize: '0.875rem'}}>{matches.length} confirmed match{matches.length !== 1 && 'es'} scheduled for donation</div>
          </div>
          <div className="status-synced">● SYNCED</div>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>DONOR (MOCK)</th>
                <th>BLOOD</th>
                <th>PATIENT</th>
                <th>HOSPITAL / CITY</th>
                <th>DATE MATCHED</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {matches.length === 0 && (
                <tr><td colSpan="6" className="text-center p-4">No confirmed matches yet.</td></tr>
              )}
              {matches.map(m => (
                <tr key={m.request_id}>
                  <td>
                    <div className="patient-name">Rahul Verma</div>
                    <div className="patient-id">Verified Donor</div>
                  </td>
                  <td><span className="blood-badge" style={{background: '#ffe4e6', color: '#e11d48'}}>{m.blood_type}</span></td>
                  <td>
                    <div className="patient-name">{m.patient_name}</div>
                    <div className="patient-id">{m.request_id}</div>
                  </td>
                  <td className="text-muted">{m.hospital}, {m.city}</td>
                  <td className="text-muted">{new Date(m.created_at).toLocaleDateString()}</td>
                  <td><span className="badge badge-scheduled">● Scheduled for Donation</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
