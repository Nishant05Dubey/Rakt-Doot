import { useState, useEffect } from 'react';
import { X, Droplet, User, MapPin, Calendar, MessageSquare, Check, XCircle } from 'lucide-react';
import './LiveCoordinationPanel.css';

export default function LiveCoordinationPanel({ patient, onClose, onConfirm }) {
  const [phase, setPhase] = useState('scanning'); // scanning, matched, chatting, confirmed
  const [donors, setDonors] = useState([]);
  const [activeDonorIndex, setActiveDonorIndex] = useState(0);
  const [chatMessages, setChatMessages] = useState([]);

  useEffect(() => {
    if (phase === 'scanning') {
      // Fetch matches from our live API
      const fetchMatches = async () => {
        try {
          const apiUrl = import.meta.env.VITE_API_URL;
          // In case API URL is not set, we'll fall back to mock data for demonstration
          if (!apiUrl) throw new Error("API URL missing");
          
          const response = await fetch(`${apiUrl}/donors/match?blood_type=${encodeURIComponent(patient.blood)}`);
          if (!response.ok) throw new Error("Failed to fetch");
          const data = await response.json();
          
          setTimeout(() => {
            if (data.matches && data.matches.length > 0) {
              setDonors(data.matches);
            } else {
              setDonors([{ donor_id: 'Mock1', name: 'Rahul Verma', distance_km: 2.1, reliability_score: 98, days_since_donation: 110 }]);
            }
            setPhase('matched');
          }, 2500); // Simulate scanning delay
        } catch (error) {
          console.error("API Error, using fallback data", error);
          setTimeout(() => {
            setDonors([
              { donor_id: 'ID1', name: 'Rahul Verma', distance_km: 4.1, reliability_score: 94, days_since_donation: 134, status: 'AVAILABLE' },
              { donor_id: 'ID2', name: 'Meena Joshi', distance_km: 6.8, reliability_score: 87, days_since_donation: 98, status: 'AT WORK' },
              { donor_id: 'ID3', name: 'Anil Kumar', distance_km: 8.2, reliability_score: 71, days_since_donation: 156, status: 'AVAILABLE' }
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
        setPhase('chatting');
        startAutomatedChat();
      }, 1500);
    }
  }, [phase]);

  const startAutomatedChat = () => {
    const sequence = [
      { sender: 'ai', text: `Namaste! 🙏 Ek Thalassemia patient ko kal ${patient.city} mein ${patient.blood} blood ki zaroorat hai. Kya aap madad kar sakte hain?`, delay: 1000 },
      { sender: 'donor', text: `Kal toh main kaam par hoon.. Sunday ko ho sakta hai?`, delay: 3500 },
      { sender: 'ai', text: `Bilkul! Sunday perfect hai. Maine aapko ${patient.hospital} mein Sunday ko subah 10 baje ke liye book kar diya hai.`, delay: 5500 },
      { sender: 'donor', text: `Theek hai, main aa jaunga 👍`, delay: 8000 },
      { sender: 'ai', text: `Bahut shukriya! Aapka ek kadam ek zindagi bachayega. 🩸 Location link aapke WhatsApp par bhej diya gaya hai.`, delay: 10000, action: 'confirm' }
    ];

    sequence.forEach((msg, idx) => {
      setTimeout(() => {
        setChatMessages(prev => [...prev, { id: idx, sender: msg.sender, text: msg.text }]);
        if (msg.action === 'confirm') {
          setTimeout(() => {
            setPhase('confirmed');
            onConfirm(patient.id);
          }, 2000);
        }
      }, msg.delay);
    });
  };

  const activeDonor = donors[activeDonorIndex] || {};

  return (
    <div className="coordination-panel-overlay">
      <div className="coordination-panel">
        <div className="panel-header">
          <div>
            <div className="panel-subtitle">LIVE COORDINATION</div>
            <h2 className="panel-title">{patient.name} <span className="blood-text">· {patient.blood} ·</span> {patient.hospital}</h2>
          </div>
          <button className="close-btn" onClick={onClose}><X size={24} /></button>
        </div>

        <div className="panel-content">
          
          {phase === 'scanning' && (
            <div className="scanning-container">
              <div className="scanning-header">
                <span className="bot-icon">🤖</span> AI Matching Engine <span className="version">v2.4</span>
              </div>
              <p className="scanning-text">Finding best donors for {patient.name}...</p>
              
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

          {phase === 'confirmed' && (
            <div className="success-banner">
              <Check size={20} /> Donor Confirmed — Dashboard Updated Automatically. No human call needed.
            </div>
          )}

          {(phase === 'matched' || phase === 'chatting' || phase === 'confirmed') && (
            <div className="donors-list">
              {donors.map((donor, idx) => {
                const isCurrentChat = idx === activeDonorIndex;
                
                if (isCurrentChat) {
                  return (
                    <div key={idx} className="active-chat-section">
                      <div className="chat-header">
                        <div className="chat-avatar">📱</div>
                        <div className="chat-title">
                          <b>{donor.name || donor.donor_id.substring(0,8)}</b>
                          <span>WhatsApp Conversation (AI Managed)</span>
                        </div>
                      </div>
                      
                      <div className="whatsapp-window">
                        <div className="wa-header">
                          <div className="wa-avatar">{donor.name ? donor.name.substring(0,2).toUpperCase() : 'RV'}</div>
                          <div className="wa-info">
                            <b>{donor.name || donor.donor_id.substring(0,8)}</b>
                            <span>● online · AI bot active</span>
                          </div>
                        </div>
                        <div className="wa-body">
                          {chatMessages.map(msg => (
                            <div key={msg.id} className={`wa-bubble ${msg.sender === 'ai' ? 'wa-ai' : 'wa-donor'}`}>
                              {msg.text}
                              {msg.sender === 'ai' && <div className="wa-tick">✓✓</div>}
                            </div>
                          ))}
                          {phase === 'chatting' && chatMessages.length > 0 && chatMessages[chatMessages.length - 1].sender === 'ai' && (
                            <div className="wa-typing">typing...</div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                }

                // Inactive donors in the queue
                return (
                  <div key={idx} className="donor-card-queued">
                    <div className="donor-rank">#{idx + 1}</div>
                    <div className="donor-card-body">
                      <div className="d-row-1">
                        <b>{donor.name || donor.donor_id.substring(0,8)}</b>
                        <span className="blood-badge-sm">{patient.blood}</span>
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
