import { useState, useEffect } from 'react';
import Header from '../components/Header';
import LiveCoordinationPanel from '../components/LiveCoordinationPanel';
import { Droplet, Heart, AlertTriangle, CheckCircle } from 'lucide-react';
import './Overview.css';

export default function Overview() {
  const [patients, setPatients] = useState([]);
  const [stats, setStats] = useState({
    total_active_donors: 0,
    lives_impacted: 0,
    urgent_pending: 0
  });

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        if (!apiUrl) return;
        const res = await fetch(`${apiUrl}/admin/dashboard`);
        if (res.ok) {
          const data = await res.json();
          setStats({
            total_active_donors: data.total_active_donors,
            lives_impacted: data.lives_impacted,
            urgent_pending: data.urgent_pending
          });
          setPatients(data.patient_queue || []);
        }
      } catch (err) {
        console.error('Failed to fetch dashboard', err);
      }
    };
    
    fetchDashboard();
    
    // Auto-refresh every 3 seconds to catch live WhatsApp/Vapi confirmations
    const intervalId = setInterval(fetchDashboard, 3000);
    return () => clearInterval(intervalId);
  }, []);

  const [activePatient, setActivePatient] = useState(null);

  const handleActivateAI = (patient) => {
    setActivePatient(patient);
  };

  const handleConfirmDonor = async (id) => {
    // Optimistic UI update
    setPatients(prev => prev.map(p => p.request_id === id ? { ...p, status: 'confirmed' } : p));
    
    // Send to live API to persist confirmation so Donor Pods and Live Feed pick it up
    try {
      const apiUrl = import.meta.env.VITE_API_URL;
      if (apiUrl) {
        await fetch(`${apiUrl}/donor/respond`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ request_id: id, response_status: 'Accepted' })
        });
      }
    } catch (err) {
      console.error('Failed to save confirmation to backend', err);
    }
    
    setTimeout(() => {
      setActivePatient(null);
    }, 2000);
  };

  const renderUrgencyBadge = (urgency) => {
    switch (urgency) {
      case 'Critical': return <span className="badge badge-critical">● Critical (6 Days)</span>;
      case 'Urgent': return <span className="badge badge-urgent">● Urgent (3 Days)</span>;
      case 'Needy': return <span className="badge badge-scheduled">● Needy (10 Days)</span>;
      default: return null;
    }
  };

  return (
    <div className="animate-fade-in">
      <Header title="Live Donor Coordination" subtitle="NGO COMMAND CENTER" />

      <div className="widgets-grid">
        <div className="card widget-card">
          <div className="widget-header">
            <span className="text-subtitle">TOTAL ACTIVE DONORS</span>
            <div className="icon-wrapper blood-icon"><Droplet size={20} /></div>
          </div>
          <h3 className="widget-value">{stats.total_active_donors.toLocaleString()}</h3>
          <p className="widget-trend trend-up">Live DB Sync</p>
        </div>

        <div className="card widget-card">
          <div className="widget-header">
            <span className="text-subtitle">LIVES IMPACTED</span>
            <div className="icon-wrapper heart-icon"><Heart size={20} /></div>
          </div>
          <h3 className="widget-value">{stats.lives_impacted.toLocaleString()}</h3>
          <p className="text-muted">Cumulative since inception</p>
        </div>

        <div className="card widget-card highlight-card">
          <div className="widget-header">
            <span className="text-subtitle">URGENT REQUESTS</span>
            <div className="icon-wrapper alert-icon"><AlertTriangle size={20} /></div>
          </div>
          <h3 className="widget-value">{stats.urgent_pending} <span className="text-muted" style={{fontSize: '1rem'}}>Pending</span></h3>
          <p className="text-muted">Auto-routed to AI matcher</p>
        </div>
      </div>

      <div className="card queue-section">
        <div className="queue-header">
          <div>
            <h3 className="text-h2" style={{fontSize: '1.25rem'}}>Patient Queue</h3>
            <p className="text-muted">Live thalassemia transfusion pipeline</p>
          </div>
          <span className="case-count">{patients.length} CASES</span>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>PATIENT</th>
                <th>BLOOD</th>
                <th>HOSPITAL</th>
                <th>CITY</th>
                <th>URGENCY</th>
                <th className="text-right">ACTION</th>
              </tr>
            </thead>
            <tbody>
              {patients.map((patient) => (
                <tr key={patient.request_id}>
                  <td>
                    <div className="patient-name">{patient.patient_name}</div>
                    <div className="patient-id">{patient.request_id}</div>
                  </td>
                  <td><span className="blood-badge">{patient.blood_type}</span></td>
                  <td>{patient.hospital}</td>
                  <td>{patient.city}</td>
                  <td>{renderUrgencyBadge(patient.urgency)}</td>
                  <td className="text-right">
                    {(patient.status === 'confirmed' || patient.status === 'Confirmed') ? (
                      <div className="status-confirmed animate-fade-in">
                        <CheckCircle size={16} /> Donor Confirmed
                      </div>
                    ) : (
                      <button 
                        className="btn-primary"
                        onClick={() => handleActivateAI(patient)}
                      >
                        <Droplet size={14} fill="currentColor" style={{marginRight: '6px', display: 'inline-block', verticalAlign: 'text-bottom'}} />
                        Activate Rakt Doot
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {activePatient && (
        <LiveCoordinationPanel 
          patient={activePatient}
          onClose={() => setActivePatient(null)}
          onConfirm={handleConfirmDonor}
        />
      )}
    </div>
  );
}
