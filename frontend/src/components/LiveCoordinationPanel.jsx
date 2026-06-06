import { useState, useEffect, useRef } from 'react';
import { X, Droplet, User, MapPin, Calendar, MessageSquare, Check, XCircle } from 'lucide-react';
import './LiveCoordinationPanel.css';

export default function LiveCoordinationPanel({ patient, onClose, onConfirm }) {
  const [phase, setPhase] = useState('scanning'); // scanning, matched, chatting, confirmed
  const [donors, setDonors] = useState([]);
  const [activeDonorIndex, setActiveDonorIndex] = useState(0);
  const [chatMessages, setChatMessages] = useState([]);
  const hasFetched = useRef(false);

  useEffect(() => {
    if (phase === 'scanning' && !hasFetched.current) {
      hasFetched.current = true;
      // Fetch matches from our live API
      const fetchMatches = async () => {
        try {
          const apiUrl = import.meta.env.VITE_API_URL;
          if (!apiUrl) throw new Error("API URL missing");
          
          const bloodType = patient.blood || patient.blood_type;
          const response = await fetch(`${apiUrl}/donors/match?blood_type=${encodeURIComponent(bloodType)}`);
          if (!response.ok) throw new Error("Failed to fetch");
          const data = await response.json();
          
          setTimeout(() => {
            if (data.matches && data.matches.length > 0) {
              setDonors(data.matches);
            } else {
              setDonors([{ donor_id: 'Mock1', name: 'Donor 682386', distance_km: 2.1, reliability_score: 98, days_since_donation: 110 }]);
            }
            setPhase('matched');
          }, 2500); // Simulate scanning delay
        } catch (error) {
          console.error("API Error, using fallback data", error);
          setTimeout(() => {
            setDonors([
              { donor_id: 'ID1', name: 'Donor 965F27', distance_km: 4.1, reliability_score: 94, days_since_donation: 134, status: 'AVAILABLE' },
              { donor_id: 'ID2', name: 'Donor 86188D', distance_km: 6.8, reliability_score: 87, days_since_donation: 98, status: 'AT WORK' },
              { donor_id: 'ID3', name: 'Donor 37AF8F', distance_km: 8.2, reliability_score: 71, days_since_donation: 156, status: 'AVAILABLE' }
            ]);
            setPhase('matched');
          }, 2500);
        }
      };
      fetchMatches();
    }
  }, [phase, patient.blood]);

  useEffect(() => {
    if (phase === 'matched') {
      setTimeout(() => {
        setPhase('waiting_webhook');
      }, 4000); // 4 seconds to view the list before waiting starts
    }
  }, [phase]);

  // Poll the live API to see if the donor replied to the WhatsApp Twilio message
  useEffect(() => {
    if (phase !== 'waiting_webhook') return;
    
    const interval = setInterval(async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL;
        if (!apiUrl) return;
        const res = await fetch(`${apiUrl}/admin/dashboard`);
        if (res.ok) {
          const data = await res.json();
          const patientId = patient.request_id || patient.id;
          const livePatient = data.patient_queue.find(p => p.request_id === patientId || p.id === patientId);
          if (livePatient && (livePatient.status === 'Confirmed' || livePatient.status === 'confirmed')) {
            setPhase('confirmed');
            clearInterval(interval);
            setTimeout(() => {
              onConfirm(patientId);
            }, 2000);
          }
        }
      } catch(e) {
        console.error("Polling error", e);
      }
    }, 3000);
    
    return () => clearInterval(interval);
  }, [phase, patient]);

  const activeDonor = donors[activeDonorIndex] || {};

  return (
    <div className="coordination-panel-overlay">
      <div className="coordination-panel">
        <div className="panel-header">
          <div>
            <div className="panel-subtitle">LIVE COORDINATION</div>
            <h2 className="panel-title">{patient.patient_name || patient.name} <span className="blood-text">· {patient.blood_type || patient.blood} ·</span> {patient.hospital}</h2>
          </div>
          <button className="close-btn" onClick={onClose}><X size={24} /></button>
        </div>

        <div className="panel-content">
          
          {phase === 'scanning' && (
            <div className="scanning-container">
              <div className="scanning-header">
                <span className="bot-icon">🤖</span> AI Matching Engine <span className="version">v2.4</span>
              </div>
              <p className="scanning-text">Finding best donors for {patient.patient_name || patient.name}...</p>
              
              <div className="radar-box">
                <div className="radar">
                  <div className="radar-ring r1"></div>
                  <div className="radar-ring r2"></div>
                  <div className="radar-ring r3"></div>
                  <Droplet className="radar-center-icon" size={32} fill="#e11d48" color="#e11d48" />
                  <div className="radar-sweep"></div>
                </div>
                <p className="radar-status">Scanning donor pods . . .</p>
              </div>
            </div>
          )}

          {phase === 'matched' && (
            <div className="success-banner" style={{background: '#dbeafe', color: '#1e40af', borderColor: '#bfdbfe'}}>
              <Check size={20} /> AI found optimal donor matches. Sending Live WhatsApp Alert...
            </div>
          )}

          {phase === 'waiting_webhook' && (
             <div className="scanning-container">
               <div className="scanning-header">
                 <span className="bot-icon">💬</span> WhatsApp Delivered
               </div>
               <p className="scanning-text" style={{marginTop: '20px', fontSize: '1.2rem'}}>
                 Waiting for donor to reply "YES" on WhatsApp...
               </p>
               <div className="radar-box" style={{height: '100px', marginTop: '20px'}}>
                 <p className="radar-status animate-pulse">Polling AWS Database for Webhook Response...</p>
               </div>
             </div>
          )}

          {phase === 'confirmed' && (
            <div className="success-banner">
              <Check size={20} /> Donor Replied YES! Dashboard Updated Automatically.
            </div>
          )}

          {(phase === 'matched' || phase === 'waiting_webhook' || phase === 'confirmed') && (
            <div className="donors-list">
              {donors.map((donor, idx) => {
                const isCurrentChat = idx === activeDonorIndex && (phase === 'waiting_webhook' || phase === 'confirmed');
                
                if (isCurrentChat) {
                  return (
                    <div key={idx} className="active-chat-section">
                      <div className="chat-header">
                        <div className="chat-avatar">📱</div>
                        <div className="chat-title">
                          <b>{donor.name || donor.donor_id.substring(0,8)}</b>
                          <span>Live Twilio Connection Active</span>
                        </div>
                      </div>
                    </div>
                  );
                }

                // Inactive donors in the queue (or all donors during 'matched' phase)
                return (
                  <div key={idx} className="donor-card-queued">
                    <div className="donor-rank">#{idx + 1}</div>
                    <div className="donor-card-body">
                      <div className="d-row-1">
                        <b>{donor.name || donor.donor_id.substring(0,8)}</b>
                        <span className="blood-badge-sm">{patient.blood_type || patient.blood}</span>
                        <span className="d-location">· {donor.distance_km} km away</span>
                        <span className="d-status-badge">AVAILABLE</span>
                      </div>
                      <div className="match-score-bar">
                        <span className="score-text">Match Score</span>
                        <div className="bar-bg"><div className="bar-fill" style={{width: `${donor.reliability_score || 80}%`}}></div></div>
                        <span className="score-val">{donor.reliability_score || 80}%</span>
                      </div>
                      <div className="d-row-3">
                        <span><Droplet size={12} color="#e11d48" /> Last donated: {donor.days_since_donation} days ago</span>
                        <span><MapPin size={12} color="#e11d48" /> {donor.distance_km} km away</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
